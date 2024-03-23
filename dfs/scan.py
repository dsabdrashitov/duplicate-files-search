import logging
from pathlib import Path, PurePosixPath
import os
import hashlib
from typing import List
from .database import DatabaseConnection, ARG_BASE_PATH

_logger = logging.getLogger(__name__)

_BUFFER_SIZE = 65536


def _normal(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _process_file(db, base: Path, file_path: Path, progress: List[int]) -> None:
    size = os.path.getsize(file_path)
    _logger.info(f"{file_path} is file. size = {size}. calculating checksum")
    h = hashlib.md5()
    print('[', end='', flush=True)
    with file_path.open("rb") as f:
        done = 0
        done_p = 0
        while True:
            buf = f.read(min(size, _BUFFER_SIZE))
            if not buf:
                break
            h.update(buf)
            done = done + len(buf)
            need_p = done * 25 // size
            if done_p < need_p:
                print('.' * (need_p - done_p), end='', flush=True)
                done_p = need_p
    print(']')
    hash_hex = h.hexdigest()
    record_path = _normal(file_path, base)
    db.Hashes.record(record_path, False, 1, size, hash_hex)
    _logger.info(f"{record_path}: {hash_hex}")
    progress[0] = progress[0] + size
    if progress[1] > 0:
        _logger.info(f"progress {progress[0]} of {progress[1]} ({progress[0] * 100 / progress[1]:.2f}%)")
    else:
        _logger.info(f"progress {progress[0]} of ? (--%)")


def _process_dir(db, base: Path, p: Path, progress: List[int], ignore: set):
    _logger.info(f"{p} is dir. traversing")
    for child in p.iterdir():
        _scan_path(db, base, child, progress, ignore)
    _logger.info(f"{p} done")


def _scan_path(db, base: Path, p: Path, progress: List[int], ignore: set = None) -> None:
    assert p.is_absolute()
    if ignore and (str(p) in ignore):
        _logger.info(f"{p} ignored.")
        return
    if p.is_file():
        _process_file(db, base, p, progress)
    elif p.is_dir():
        _process_dir(db, base, p, progress, ignore)


def _calc_size(p: Path, ignore=None) -> int:
    result = 0
    if ignore and (str(p) in ignore):
        pass
    elif p.is_file():
        result = os.path.getsize(p)
    elif p.is_dir():
        for child in p.iterdir():
            result = result + _calc_size(child, ignore)
    return result


def scan(db_file, path: str):
    db = DatabaseConnection(db_file)
    try:
        base = Path(db.Info.get_value(ARG_BASE_PATH))
        ignore = {str(Path(db_file).absolute())}
        total_size = _calc_size(Path(path).absolute(), ignore=ignore)

        # remove all prefixes
        prefix = _normal(Path(path).absolute(), base)
        prefix_dir = PurePosixPath(prefix)
        potential_children = [hash_row for hash_row in db.Hashes.select().where(db.Hashes.path.startswith(prefix))]
        for pc in potential_children:
            if PurePosixPath(pc.path).is_relative_to(prefix_dir):
                _logger.info(f"Remove item for: {pc.path}, debug:{prefix_dir}")
                db.Hashes.delete().where(db.Hashes.path == pc.path)

        _scan_path(db, base, Path(path).absolute(), progress=[0, total_size], ignore=ignore)
    finally:
        db.close()
    _logger.info(f"scan {path} to {db_file} done")
