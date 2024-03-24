import logging
from typing import Optional, List
from peewee import SqliteDatabase, Model, CharField, BigIntegerField, BooleanField
from pathlib import Path

FORMAT_VERSION = "0.0.4"

ARG_FORMAT_VERSION = "version"
ARG_BASE_PATH = "base"

_logger = logging.getLogger(__name__)


def _bind_hashes(db):

    class Hashes(Model):
        path = CharField(primary_key=True)
        is_dir = BooleanField()
        count = BigIntegerField()
        size = BigIntegerField()
        hash_hex = CharField(index=True)

        class Meta:
            database = db

        @staticmethod
        def record(path: str, is_dir: bool, count: int, size: int, hash_hex: str):
            Hashes.replace(path=path, is_dir=is_dir, count=count, size=size, hash_hex=hash_hex).execute()

    return Hashes


def _bind_hash_cache(db):

    class HashCache(Model):
        path = CharField(primary_key=True)
        hash_hex = CharField()

        class Meta:
            database = db

        @staticmethod
        def record(path, hash_hex):
            HashCache.replace(path=path, hash_hex=hash_hex).execute()

        @staticmethod
        def find_cache(path: str) -> Optional[str]:
            row = HashCache.get_or_none(HashCache.path == path)
            if row is None:
                return None
            else:
                return row.hash_hex

        @staticmethod
        def clear() -> None:
            HashCache.delete().execute()

    return HashCache


def _bind_ignore_scan(db):

    class IgnoreScan(Model):
        path = CharField(primary_key=True)

        class Meta:
            database = db

        @staticmethod
        def add_ignore(path: str):
            IgnoreScan.replace(path=path).execute()

        @staticmethod
        def remove_ignore(path: str):
            IgnoreScan.delete().where(IgnoreScan.path == path).execute()

        @staticmethod
        def list_ignore() -> List[str]:
            return [row.path for row in IgnoreScan.select()]

    return IgnoreScan


def _bind_info(db):

    class Info(Model):
        arg = CharField(primary_key=True)
        value = CharField()

        class Meta:
            database = db

        @staticmethod
        def get_value(arg):
            row = Info.get_or_none(Info.arg == arg)
            if row is None:
                return None
            return str(row.value)

        @staticmethod
        def set_value(arg, value):
            Info.replace(arg=arg, value=value).execute()

    return Info


class DatabaseConnection:

    def __init__(self, filename, create_new=False):
        existed = Path(filename).exists()
        if existed and create_new:
            raise RuntimeError(f"{filename} already exists")
        if (not existed) and (not create_new):
            raise RuntimeError(f"{filename} not exists")

        self.db = SqliteDatabase(filename)
        try:
            self.Info = _bind_info(self.db)
            self.Hashes = _bind_hashes(self.db)
            self.HashCache = _bind_hash_cache(self.db)
            self.IgnoreScan = _bind_ignore_scan(self.db)

            if not existed:
                self.db.create_tables([
                    self.Info,
                    self.Hashes,
                    self.HashCache,
                    self.IgnoreScan,
                ])
                self.Info.set_value(ARG_FORMAT_VERSION, FORMAT_VERSION)

            version = self.Info.get_value(ARG_FORMAT_VERSION)
            if version != FORMAT_VERSION:
                raise RuntimeError(f"incompatible version - {version} instead of {FORMAT_VERSION}")
        except RuntimeError as e:
            self.db.close()
            raise e

    def close(self):
        self.db.close()
