from peewee import AutoField, CharField, ForeignKeyField

from src.database.database import BaseModel


class Genre(BaseModel):
    id = AutoField()
    name = CharField(max_length=100, null=False, unique=True)
    parent = ForeignKeyField('self', null=True, backref='children', on_delete='SET NULL')

    class Meta:
        db_table = 'genres'
