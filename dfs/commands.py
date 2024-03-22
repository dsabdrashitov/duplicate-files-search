import logging
from .database import DatabaseConnection

_logger = logging.getLogger(__name__)


def init(db_file):
    db = DatabaseConnection(db_file)
    db.close()
    _logger.info(f"touched db at: {db_file}")
