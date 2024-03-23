import logging
from pathlib import Path
import os
import hashlib
from .database import DatabaseConnection, ARG_BASE_PATH

_logger = logging.getLogger(__name__)

_BUFFER_SIZE = 65536


def _normal(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _process_file(db, base: Path, file_path: Path) -> None:
    size = os.path.getsize(file_path)
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
    _logger.info(f"{record_path}({size}): {hash_hex}")


def _scan_path(db, base: Path, p: Path, ignore=None):
    assert p.is_absolute()
    if str(p) in ignore:
        _logger.info(f"{p} ignored.")
        return
    if p.is_file():
        _logger.info(f"{p} is file. calculating checksum")
        _process_file(db, base, p)
    elif p.is_dir():
        _logger.info(f"{p} is dir. traversing")
        for child in p.iterdir():
            _scan_path(db, base, child, ignore)
        _logger.info(f"{p} done")


def scan(db_file, path: str):
    db = DatabaseConnection(db_file)
    base = Path(db.Info.get_value(ARG_BASE_PATH))
    ignore = {str(Path(db_file).absolute())}
    try:
        _scan_path(db, base, Path(path).absolute(), ignore=ignore)
    finally:
        db.close()
    _logger.info(f"scan {path} to {db_file} done")
