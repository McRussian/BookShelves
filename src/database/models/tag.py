from peewee import AutoField, CharField, fn, ModelSelect

from src.database.database import BaseModel


class Tag(BaseModel):
    id = AutoField()
    name = CharField(max_length=50, null=False, unique=True)

    class Meta:
        db_table = 'tags'

    @classmethod
    def search(cls, query: str) -> ModelSelect:
        """Поиск по названию тега, без учёта регистра, по подстроке."""
        return cls.select().where(fn.LOWER(cls.name).contains(query.lower()))
