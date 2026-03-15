from pathlib import Path
from peewee import Model, SqliteDatabase, DatabaseProxy

database_proxy = DatabaseProxy()


def init_db(db_path: Path) -> SqliteDatabase:
    db = SqliteDatabase(db_path, pragmas={'journal_mode': 'wal', 'foreign_keys': 1})
    database_proxy.initialize(db)
    return db


class BaseModel(Model):
    class Meta:
        database = database_proxy
