import unittest
from peewee import IntegrityError

from src.database.models.author import Author
from src.database.models.book import Book, BookAuthor, BookGenre, BookTag
from src.database.models.book_format import BookFormat
from src.database.models.edition import Edition
from src.database.models.genre import Genre
from src.database.models.publisher import Publisher
from src.database.models.tag import Tag
from tests.database.conftest import BaseTestCase


class TestBookCreate(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.fmt = BookFormat.create(name='epub')
        self.publisher = Publisher.create(name='АСТ')
        self.edition = Edition.create(name='Первое издание')
        self.book = Book.create(
            title='Тёмная башня',
            file_path='/books/dark_tower.epub',
            file_size=1024000,
            pages=500,
            year=1982,
            format=self.fmt,
            edition=self.edition,
            publisher=self.publisher,
            comment='Первая книга цикла',
        )

    def test_create_full(self):
        saved = Book.get_by_id(self.book.id)
        self.assertEqual(saved.title, 'Тёмная башня')
        self.assertEqual(saved.pages, 500)
        self.assertEqual(saved.year, 1982)
        self.assertEqual(saved.file_size, 1024000)
        self.assertEqual(saved.format.name, 'epub')
        self.assertEqual(saved.publisher.name, 'АСТ')
        self.assertEqual(saved.edition.name, 'Первое издание')

    def test_create_minimal(self):
        book = Book.create(title='Без метаданных', file_path='/books/unknown.epub')
        saved = Book.get_by_id(book.id)
        self.assertIsNone(saved.pages)
        self.assertIsNone(saved.year)
        self.assertIsNone(saved.format_id)

    def test_unique_file_path(self):
        with self.assertRaises(IntegrityError):
            Book.create(title='Другая книга', file_path='/books/dark_tower.epub')

    def test_delete(self):
        self.book.delete_instance()
        self.assertEqual(Book.select().count(), 0)


class TestBookAuthor(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.book = Book.create(title='Тёмная башня', file_path='/books/b.epub')

    def test_add_author(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        BookAuthor.create(book=self.book, author=author)
        self.assertEqual(BookAuthor.select().where(BookAuthor.book == self.book).count(), 1)

    def test_multiple_authors(self):
        a1 = Author.create(firstname='Илья', lastname='Ильф')
        a2 = Author.create(firstname='Евгений', lastname='Петров')
        BookAuthor.create(book=self.book, author=a1)
        BookAuthor.create(book=self.book, author=a2)
        self.assertEqual(BookAuthor.select().where(BookAuthor.book == self.book).count(), 2)

    def test_unique_constraint(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        BookAuthor.create(book=self.book, author=author)
        with self.assertRaises(IntegrityError):
            BookAuthor.create(book=self.book, author=author)

    def test_one_author_multiple_books(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        book2 = Book.create(title='Оно', file_path='/books/it.epub')
        BookAuthor.create(book=self.book, author=author)
        BookAuthor.create(book=book2, author=author)
        self.assertEqual(BookAuthor.select().where(BookAuthor.author == author).count(), 2)


class TestBookGenre(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.book = Book.create(title='Тёмная башня', file_path='/books/b.epub')

    def test_add_genre(self):
        genre = Genre.create(name='Фантастика')
        BookGenre.create(book=self.book, genre=genre)
        self.assertEqual(BookGenre.select().where(BookGenre.book == self.book).count(), 1)

    def test_multiple_genres(self):
        g1 = Genre.create(name='Фантастика')
        g2 = Genre.create(name='Ужасы')
        BookGenre.create(book=self.book, genre=g1)
        BookGenre.create(book=self.book, genre=g2)
        self.assertEqual(BookGenre.select().where(BookGenre.book == self.book).count(), 2)

    def test_unique_constraint(self):
        genre = Genre.create(name='Фантастика')
        BookGenre.create(book=self.book, genre=genre)
        with self.assertRaises(IntegrityError):
            BookGenre.create(book=self.book, genre=genre)


class TestBookTag(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.book = Book.create(title='Тёмная башня', file_path='/books/b.epub')

    def test_add_tag(self):
        tag = Tag.create(name='мистика')
        BookTag.create(book=self.book, tag=tag)
        self.assertEqual(BookTag.select().where(BookTag.book == self.book).count(), 1)

    def test_multiple_tags(self):
        for name in ('мистика', 'ужасы', 'фэнтези'):
            BookTag.create(book=self.book, tag=Tag.create(name=name))
        self.assertEqual(BookTag.select().where(BookTag.book == self.book).count(), 3)

    def test_unique_constraint(self):
        tag = Tag.create(name='мистика')
        BookTag.create(book=self.book, tag=tag)
        with self.assertRaises(IntegrityError):
            BookTag.create(book=self.book, tag=tag)


class TestBookCascade(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.book = Book.create(title='Тёмная башня', file_path='/books/b.epub')
        self.author = Author.create(firstname='Стивен', lastname='Кинг')
        self.genre = Genre.create(name='Ужасы')
        self.tag = Tag.create(name='мистика')
        BookAuthor.create(book=self.book, author=self.author)
        BookGenre.create(book=self.book, genre=self.genre)
        BookTag.create(book=self.book, tag=self.tag)

    def test_delete_book_cascades_relations(self):
        self.book.delete_instance()
        self.assertEqual(BookAuthor.select().count(), 0)
        self.assertEqual(BookGenre.select().count(), 0)
        self.assertEqual(BookTag.select().count(), 0)
        # Справочники остаются
        self.assertEqual(Author.select().count(), 1)
        self.assertEqual(Genre.select().count(), 1)
        self.assertEqual(Tag.select().count(), 1)

    def test_delete_author_removes_relation_not_book(self):
        self.author.delete_instance()
        self.assertEqual(Book.select().count(), 1)
        self.assertEqual(BookAuthor.select().count(), 0)

    def test_delete_format_sets_null_on_book(self):
        fmt = BookFormat.create(name='epub')
        self.book.format = fmt
        self.book.save()
        fmt.delete_instance()
        reloaded = Book.get_by_id(self.book.id)
        self.assertIsNone(reloaded.format_id)

    def test_delete_publisher_sets_null_on_book(self):
        pub = Publisher.create(name='АСТ')
        self.book.publisher = pub
        self.book.save()
        pub.delete_instance()
        reloaded = Book.get_by_id(self.book.id)
        self.assertIsNone(reloaded.publisher_id)


if __name__ == '__main__':
    unittest.main()
