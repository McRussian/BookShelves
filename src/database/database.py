from pathlib import Path
from peewee import Model, SqliteDatabase, DatabaseProxy

database_proxy = DatabaseProxy()


def init_db(db_path: Path) -> SqliteDatabase:
    db = SqliteDatabase(db_path, pragmas={'foreign_keys': 1}, timeout=30)
    database_proxy.initialize(db)
    return db


def create_db(db_path: Path) -> None:
    """Создать пустой файл БД, удалив старый вместе с WAL/SHM файлами."""
    for p in (db_path,
              db_path.with_name(db_path.name + '-wal'),
              db_path.with_name(db_path.name + '-shm')):
        p.unlink(missing_ok=True)


class BaseModel(Model):
    class Meta:
        database = database_proxy
