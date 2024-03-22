import logging
from peewee import SqliteDatabase, Model, CharField

_VERSION = "version"
FORMAT_VERSION = "0.0.1"

_logger = logging.getLogger(__name__)


def _bind_hashes(db):

    class Hashes(Model):
        path = CharField(primary_key=True)
        hash = CharField(index=True)

        class Meta:
            database = db

    return Hashes


def _bind_info(db):

    class Info(Model):
        arg = CharField(primary_key=True)
        value = CharField()

        class Meta:
            database = db

    return Info


class DatabaseConnection:

    def __init__(self, filename):
        self.db = SqliteDatabase(filename)
        try:
            self.Info = _bind_info(self.db)

            self.db.create_tables([self.Info])
            version = self.Info.get_or_none(self.Info.arg == _VERSION)
            if version is None:
                version = self.Info.create(arg=_VERSION, value=FORMAT_VERSION)
            if version.value != FORMAT_VERSION:
                raise RuntimeError(f"incompatible version - {version.value} instead of {FORMAT_VERSION}")
            self.Hashes = _bind_hashes(self.db)

            self.db.create_tables([self.Hashes])
        except RuntimeError:
            self.db.close()

    def close(self):
        self.db.close()
