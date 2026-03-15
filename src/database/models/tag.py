from peewee import AutoField, CharField

from src.database.database import BaseModel


class Tag(BaseModel):
    id = AutoField()
    name = CharField(max_length=50, null=False, unique=True)

    class Meta:
        db_table = 'tags'
