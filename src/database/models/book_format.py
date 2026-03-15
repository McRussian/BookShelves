from peewee import AutoField, CharField

from src.database.database import BaseModel


class BookFormat(BaseModel):
    id = AutoField()
    name = CharField(max_length=20, null=False, unique=True)  # epub, pdf, fb2, mobi...

    class Meta:
        db_table = 'book_formats'
