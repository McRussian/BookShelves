from pathlib import Path
from peewee import Model, SqliteDatabase


class DataBase:
    db: SqliteDatabase


def init_db(db_path: Path):
    DataBase.db = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = DataBase.db

