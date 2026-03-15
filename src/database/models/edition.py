from peewee import AutoField, CharField

from src.database.database import BaseModel


class Edition(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False, unique=True)

    class Meta:
        db_table = 'editions'
