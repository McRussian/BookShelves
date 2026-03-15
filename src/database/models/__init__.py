from src.database.models.author import Author, AuthorAlias
from src.database.models.book import Book, BookAuthor, BookGenre, BookTag
from src.database.models.book_format import BookFormat
from src.database.models.edition import Edition
from src.database.models.genre import Genre
from src.database.models.publisher import Publisher
from src.database.models.tag import Tag

ALL_MODELS = [
    Author,
    AuthorAlias,
    Genre,
    Tag,
    BookFormat,
    Edition,
    Publisher,
    Book,
    BookAuthor,
    BookGenre,
    BookTag,
]
