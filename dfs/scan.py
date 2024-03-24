import logging
from pathlib import Path, PurePosixPath
import os
import hashlib
from typing import List
from .database import DatabaseConnection, ARG_BASE_PATH

_logger = logging.getLogger(__name__)

_BUFFER_SIZE = 65536
_PROGRESS_DOTS = 25


def _normal(path: Path, base: Path) -> str:
    result = path.relative_to(base).as_posix()
    if result == '.':
        result = ''
    return result


def _process_file(db, base: Path, file_path: Path, progress: List[int], fast: bool) -> None:
    size = os.path.getsize(file_path)
    record_path = _normal(file_path, base)
    _logger.info(f"{file_path} is file. size = {size}. calculating checksum")
    print('[', end='', flush=True)
    cached = db.HashCache.find_cache(record_path)
    if fast and (cached is not None):
        print('c' * _PROGRESS_DOTS, end='')
        hash_hex = cached
    else:
        h = hashlib.md5()
        with file_path.open("rb") as f:
            done = 0
            done_p = 0
            while True:
                buf = f.read(min(size, _BUFFER_SIZE))
                if not buf:
                    break
                h.update(buf)
                done = done + len(buf)
                need_p = done * _PROGRESS_DOTS // size
                if done_p < need_p:
                    print('.' * (need_p - done_p), end='', flush=True)
                    done_p = need_p
        hash_hex = h.hexdigest()
    print(']')
    db.Hashes.record(record_path, False, 1, size, hash_hex)
    _logger.info(f"{record_path}: {hash_hex}")
    progress[0] = progress[0] + size
    if progress[1] > 0:
        _logger.info(f"progress {progress[0]} of {progress[1]} ({progress[0] * 100 / progress[1]:.2f}%)")
    else:
        _logger.info(f"progress {progress[0]} of ? (--%)")


def _process_dir(db, base: Path, p: Path, progress: List[int], ignore: set, fast: bool):
    _logger.info(f"{p} is dir. traversing")
    dir_row = db.Hashes(
        path=_normal(p, base),
        is_dir=True,
        count=0,
        size=0,
        hash_hex="",
    )
    hash_list = []
    for child in p.iterdir():
        _scan_path(db, base, child, progress, ignore, fast)
        if (not ignore) or (str(child) not in ignore):
            child_row = db.Hashes.get(db.Hashes.path == _normal(child, base))
            dir_row.count = dir_row.count + child_row.count
            dir_row.size = dir_row.size + child_row.size
            hash_list.append([child.name, child_row.hash_hex])
    hash_list.sort(key=lambda e: e[0])
    dir_str = "".join([f"{e[0]},{e[1]}\n" for e in hash_list])
    dir_row.hash_hex = hashlib.md5(dir_str.encode("utf-8")).hexdigest()
    dir_row.save(force_insert=True)
    _logger.info(f"{p} done")


def _scan_path(db, base: Path, p: Path, progress: List[int], ignore: set, fast: bool) -> None:
    assert p.is_absolute()
    if ignore and (str(p) in ignore):
        _logger.info(f"{p} ignored.")
        return
    if p.is_file():
        _process_file(db, base, p, progress, fast)
    elif p.is_dir():
        _process_dir(db, base, p, progress, ignore, fast)


def _calc_size(p: Path, ignore=None) -> int:
    _logger.info(f"calculating size of {p}")
    result = 0
    if ignore and (str(p) in ignore):
        pass
    elif p.is_file():
        result = os.path.getsize(p)
    elif p.is_dir():
        for child in p.iterdir():
            result = result + _calc_size(child, ignore)
    return result


def scan(db_file, path: str, fast: bool = False):
    db = DatabaseConnection(db_file)
    try:
        base = Path(db.Info.get_value(ARG_BASE_PATH))
        ignore = {str(Path(db_file).absolute())}
        ignore.update(db.IgnoreScan.list_ignore())
        total_size = _calc_size(Path(path).absolute(), ignore=ignore)

        # remove all prefixes
        prefix = _normal(Path(path).absolute(), base)
        prefix_dir = PurePosixPath(prefix)
        potential_children = [hash_row for hash_row in db.Hashes.select().where(db.Hashes.path.startswith(prefix))]
        for pc in potential_children:
            if PurePosixPath(pc.path).is_relative_to(prefix_dir):
                _logger.info(f"Remove item for: {pc.path}")
                db.HashCache.record(path=pc.path, hash_hex=pc.hash_hex)
                pc.delete_instance()

        _scan_path(db, base, Path(path).absolute(), progress=[0, total_size], ignore=ignore, fast=fast)
        db.HashCache.clear()
    finally:
        db.close()
    _logger.info(f"scan {path} to {db_file} done")
