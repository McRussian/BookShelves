from pathlib import Path
from peewee import Model, SqliteDatabase, DatabaseProxy

database_proxy = DatabaseProxy()


def init_db(db_path: Path) -> SqliteDatabase:
    db = SqliteDatabase(db_path, pragmas={'foreign_keys': 1}, timeout=30)
    database_proxy.initialize(db)
    return db


def create_db(db_path: Path) -> SqliteDatabase:
    """Create a new DB file and enable WAL mode (persistent, set once)."""
    db = init_db(db_path)
    db.connect()
    db.execute_sql('PRAGMA journal_mode=wal')
    db.close()
    return db


class BaseModel(Model):
    class Meta:
        database = database_proxy
