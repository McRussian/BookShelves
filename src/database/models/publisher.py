from peewee import AutoField, CharField, fn, ModelSelect

from src.database.database import BaseModel


class Publisher(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, null=False, unique=True)
    comment = CharField(max_length=500, null=True)

    class Meta:
        db_table = 'publishers'

    @classmethod
    def search(cls, query: str) -> ModelSelect:
        return (cls.select()
                .where(fn.LOWER(cls.name).contains(query.lower()))
                .order_by(cls.name))
