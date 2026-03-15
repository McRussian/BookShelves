from peewee import AutoField, CharField

from src.database.database import BaseModel


class Publisher(BaseModel):
    id = AutoField()
    name = CharField(max_length=200, null=False)
    comment = CharField(max_length=500, null=True)

    class Meta:
        db_table = 'publishers'
