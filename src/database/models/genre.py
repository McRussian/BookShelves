from peewee import AutoField, CharField, fn, ForeignKeyField, ModelSelect

from src.database.database import BaseModel


class Genre(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False, unique=True)
    parent = ForeignKeyField('self', null=True, backref='children', on_delete='SET NULL')

    class Meta:
        db_table = 'genres'

    @classmethod
    def search(cls, query: str) -> ModelSelect:
        """Поиск по названию жанра, без учёта регистра, по подстроке."""
        return cls.select().where(fn.LOWER(cls.name).contains(query.lower()))
