import logging
from pathlib import Path
import hashlib
from .database import DatabaseConnection

_logger = logging.getLogger(__name__)

_BUFFER_SIZE = 65536


def init(db_file):
    db = DatabaseConnection(db_file)
    db.close()
    _logger.info(f"touched db at: {db_file}")


def _calc_hash(p) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        while True:
            buf = f.read(_BUFFER_SIZE)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def _scan_path(db, p: Path, ignore=None):
    k = str(p.absolute())
    if k in ignore:
        _logger.info(f"{k} ignored.")
        return
    if p.is_file():
        _logger.info(f"{k} is file. calculating checksum")
        h = _calc_hash(p)
        db.Hashes.replace(path=k, hash=h).execute()
        _logger.info(f"{k} hash = {h}")
    elif p.is_dir():
        _logger.info(f"{k} is dir. traversing")
        for child in p.iterdir():
            _scan_path(db, child, ignore)
        _logger.info(f"{k} done")


def scan(db_file, path: str):
    db = DatabaseConnection(db_file)
    ignore = {str(Path(db_file).absolute())}
    try:
        _scan_path(db, Path(path), ignore=ignore)
    finally:
        db.close()
    _logger.info(f"scan {path} to {db_file} done")
