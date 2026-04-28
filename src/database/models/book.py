from peewee import AutoField, CharField, IntegerField, ForeignKeyField, fn, JOIN, ModelSelect

from src.database.database import BaseModel
from src.database.models.author import Author, AuthorAlias
from src.database.models.book_format import BookFormat
from src.database.models.book_type import BookType
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
    book_type = ForeignKeyField(BookType, null=True, backref='books', on_delete='SET NULL')
    format = ForeignKeyField(BookFormat, null=True, backref='books', on_delete='SET NULL')
    edition = ForeignKeyField(Edition, null=True, backref='books', on_delete='SET NULL')
    publisher = ForeignKeyField(Publisher, null=True, backref='books', on_delete='SET NULL')
    comment = CharField(max_length=500, null=True)

    class Meta:
        db_table = 'books'

    @classmethod
    def search(
        cls,
        text: str = '',
        author_ids=(),
        tag_ids=(),
        genre_ids=(),
    ) -> ModelSelect:
        """Поиск книг по тексту и фильтрам.

        - text: поиск по названию И имени автора (firstname/lastname/alias).
          Каждое слово AND-ится; слова ищутся в названии ИЛИ у автора.
        - author_ids: OR — книги хотя бы одного из авторов.
        - tag_ids: OR — книги хотя бы с одним из тегов.
        - genre_ids: OR — книги хотя бы одного из жанров.
        Все непустые критерии AND-ятся между собой.
        """
        qs = cls.select()

        for word in text.lower().split():
            matching_author_ids = (
                Author.select(Author.id)
                .join(AuthorAlias, JOIN.LEFT_OUTER)
                .where(
                    fn.LOWER(Author.firstname).contains(word) |
                    fn.LOWER(Author.lastname).contains(word) |
                    fn.LOWER(Author.surname).contains(word) |
                    fn.LOWER(AuthorAlias.alias).contains(word)
                )
            )
            book_ids_by_author = (
                BookAuthor.select(BookAuthor.book)
                .where(BookAuthor.author.in_(matching_author_ids))
            )
            qs = qs.where(
                fn.LOWER(cls.title).contains(word) |
                cls.id.in_(book_ids_by_author)
            )

        if author_ids:
            qs = qs.where(
                cls.id.in_(
                    BookAuthor.select(BookAuthor.book)
                    .where(BookAuthor.author.in_(list(author_ids)))
                )
            )

        if tag_ids:
            qs = qs.where(
                cls.id.in_(
                    BookTag.select(BookTag.book)
                    .where(BookTag.tag.in_(list(tag_ids)))
                )
            )

        if genre_ids:
            qs = qs.where(
                cls.id.in_(
                    BookGenre.select(BookGenre.book)
                    .where(BookGenre.genre.in_(list(genre_ids)))
                )
            )

        return qs.order_by(fn.LOWER(cls.title))


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
