from peewee import CharField, PrimaryKeyField
from src.database.database import BaseModel


class Author(BaseModel):
    id = PrimaryKeyField(null=False)
    firstname = CharField(max_length=30, null=False)
    lastname = CharField(max_length=30, null=False)
    surname = CharField(max_length=30)
    alias = CharField(max_length=50)
    comment = CharField(max_length=100)

    class Meta:
        db_table = "authors"
