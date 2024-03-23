import logging
from pathlib import Path
from .database import DatabaseConnection, ARG_BASE_PATH

_logger = logging.getLogger(__name__)


def init(db_file: str, base_path: str) -> None:
    if Path(db_file).exists():
        _logger.info(f"Database {db_file} already exists")
        return
    db = DatabaseConnection(db_file, create_new=True)
    db.Info.set_value(ARG_BASE_PATH, Path(base_path).absolute())
    db.close()
    _logger.info(f"created db at: {db_file}")
