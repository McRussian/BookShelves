from peewee import AutoField, CharField, IntegerField, ForeignKeyField

from src.database.database import BaseModel
from src.database.models.author import Author
from src.database.models.book_format import BookFormat
from src.database.models.edition import Edition
from src.database.models.genre import Genre
from src.database.models.publisher import Publisher
from src.database.models.tag import Tag


class Book(BaseModel):
    id = AutoField()
    title = CharField(max_length=300, null=False)
    file_path = CharField(max_length=500, null=False, unique=True)
    file_size = IntegerField(null=True)   # байты, заполняется из файла
    pages = IntegerField(null=True)
    year = IntegerField(null=True)
    format = ForeignKeyField(BookFormat, null=True, backref='books', on_delete='SET NULL')
    edition = ForeignKeyField(Edition, null=True, backref='books', on_delete='SET NULL')
    publisher = ForeignKeyField(Publisher, null=True, backref='books', on_delete='SET NULL')
    comment = CharField(max_length=500, null=True)

    class Meta:
        db_table = 'books'


class BookAuthor(BaseModel):
    book = ForeignKeyField(Book, backref='book_authors', on_delete='CASCADE')
    author = ForeignKeyField(Author, backref='book_authors', on_delete='CASCADE')

    class Meta:
        db_table = 'book_authors'
        indexes = ((('book_id', 'author_id'), True),)


class BookGenre(BaseModel):
    book = ForeignKeyField(Book, backref='book_genres', on_delete='CASCADE')
    genre = ForeignKeyField(Genre, backref='book_genres', on_delete='CASCADE')

    class Meta:
        db_table = 'book_genres'
        indexes = ((('book_id', 'genre_id'), True),)


class BookTag(BaseModel):
    book = ForeignKeyField(Book, backref='book_tags', on_delete='CASCADE')
    tag = ForeignKeyField(Tag, backref='book_tags', on_delete='CASCADE')

    class Meta:
        db_table = 'book_tags'
        indexes = ((('book_id', 'tag_id'), True),)
