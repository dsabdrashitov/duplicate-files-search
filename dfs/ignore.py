import logging
from pathlib import Path
from .database import DatabaseConnection

_logger = logging.getLogger(__name__)


def ignore_add(db_file: str, path: str):
    db = DatabaseConnection(db_file)
    try:
        abs_path = str(Path(path).absolute())
        db.IgnoreScan.add_ignore(abs_path)
    finally:
        db.close()
    _logger.info(f"{abs_path} added to ignore list")


def ignore_remove(db_file: str, path: str):
    db = DatabaseConnection(db_file)
    try:
        abs_path = str(Path(path).absolute())
        db.IgnoreScan.remove_ignore(abs_path)
    finally:
        db.close()
    _logger.info(f"{abs_path} removed from ignore list")


def ignore_list(db_file: str):
    db = DatabaseConnection(db_file)
    try:
        result = db.IgnoreScan.list_ignore()
        _logger.info(f"ignore list contains {len(result)} paths")
        for i in range(len(result)):
            _logger.info(f"ignore({i}/{len(result)}): {result[i]}")
    finally:
        db.close()
