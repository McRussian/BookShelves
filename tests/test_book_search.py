import unittest

from src.database.models.author import Author, AuthorAlias
from src.database.models.book import Book, BookAuthor, BookGenre, BookTag
from src.database.models.genre import Genre
from src.database.models.tag import Tag
from tests.database.conftest import BaseTestCase


# ── helpers ───────────────────────────────────────────────────────────────────

_book_counter = 0


def make_book(title: str, file_path: str = None) -> Book:
    global _book_counter
    _book_counter += 1
    if file_path is None:
        file_path = f'/tmp/book_{_book_counter}.pdf'
    return Book.create(title=title, file_path=file_path)


def attach_author(book: Book, author: Author) -> BookAuthor:
    return BookAuthor.create(book=book, author=author)


def attach_tag(book: Book, tag: Tag) -> BookTag:
    return BookTag.create(book=book, tag=tag)


def attach_genre(book: Book, genre: Genre) -> BookGenre:
    return BookGenre.create(book=book, genre=genre)


def result_titles(qs) -> list[str]:
    return [b.title for b in qs]


# ── TestBookSearchByText ───────────────────────────────────────────────────────

class TestBookSearchByText(BaseTestCase):

    def test_empty_text_returns_all_books(self):
        make_book('Alpha')
        make_book('Beta')
        results = Book.search(text='')
        self.assertEqual(len(list(results)), 2)

    def test_no_criteria_returns_all_books(self):
        make_book('Alpha')
        make_book('Beta')
        results = Book.search()
        self.assertEqual(len(list(results)), 2)

    def test_search_by_title_exact(self):
        make_book('Python Programming')
        make_book('Java Basics')
        results = Book.search(text='Python')
        titles = result_titles(results)
        self.assertIn('Python Programming', titles)
        self.assertNotIn('Java Basics', titles)

    def test_search_by_title_partial(self):
        make_book('Clean Code')
        make_book('Clean Architecture')
        make_book('Refactoring')
        results = Book.search(text='Clean')
        titles = result_titles(results)
        self.assertIn('Clean Code', titles)
        self.assertIn('Clean Architecture', titles)
        self.assertNotIn('Refactoring', titles)

    def test_search_by_title_case_insensitive(self):
        make_book('Design Patterns')
        results = Book.search(text='design patterns')
        self.assertEqual(len(list(results)), 1)

    def test_search_by_title_uppercase_query(self):
        make_book('Design Patterns')
        results = Book.search(text='DESIGN')
        self.assertEqual(len(list(results)), 1)

    def test_search_by_author_firstname(self):
        book = make_book('Some Book')
        author = Author.create(firstname='Стивен', lastname='Кинг')
        attach_author(book, author)
        make_book('Other Book')  # no author

        results = Book.search(text='Стивен')
        titles = result_titles(results)
        self.assertIn('Some Book', titles)
        self.assertNotIn('Other Book', titles)

    def test_search_by_author_lastname(self):
        book = make_book('The Shining')
        author = Author.create(firstname='Стивен', lastname='Кинг')
        attach_author(book, author)

        results = Book.search(text='Кинг')
        self.assertIn('The Shining', result_titles(results))

    def test_search_by_author_alias(self):
        book = make_book('Rage')
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        attach_author(book, author)

        results = Book.search(text='Бахман')
        self.assertIn('Rage', result_titles(results))

    def test_search_author_alias_partial(self):
        book = make_book('Rage')
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        attach_author(book, author)

        results = Book.search(text='Бахм')
        self.assertIn('Rage', result_titles(results))

    def test_text_matches_title_or_author(self):
        """Word in title OR author — both books should match."""
        book_by_title = make_book('Кинг-гора')
        book_by_author = make_book('The Stand')
        author = Author.create(firstname='Стивен', lastname='Кинг')
        attach_author(book_by_author, author)

        results = Book.search(text='кинг')
        titles = result_titles(results)
        self.assertIn('Кинг-гора', titles)
        self.assertIn('The Stand', titles)

    def test_multiword_and_logic(self):
        """All words must match (AND). Only book matching both words is returned."""
        book1 = make_book('Python Tricks')
        book2 = make_book('Python Basics')
        book3 = make_book('Java Tricks')

        results = Book.search(text='Python Tricks')
        titles = result_titles(results)
        self.assertIn('Python Tricks', titles)
        self.assertNotIn('Python Basics', titles)
        self.assertNotIn('Java Tricks', titles)

    def test_multiword_title_and_author(self):
        """One word matches title, another matches author."""
        book = make_book('Foundation')
        author = Author.create(firstname='Айзек', lastname='Азимов')
        attach_author(book, author)
        make_book('Dune')  # no match

        results = Book.search(text='Foundation Азимов')
        titles = result_titles(results)
        self.assertIn('Foundation', titles)
        self.assertNotIn('Dune', titles)

    def test_no_match_returns_empty(self):
        make_book('Real Book')
        results = Book.search(text='xyznonexistent')
        self.assertEqual(len(list(results)), 0)


# ── TestBookSearchByFilters ────────────────────────────────────────────────────

class TestBookSearchByFilters(BaseTestCase):

    def test_author_ids_single(self):
        book1 = make_book('Book by King')
        book2 = make_book('Book by Tolstoy')
        king = Author.create(firstname='Стивен', lastname='Кинг')
        tolstoy = Author.create(firstname='Лев', lastname='Толстой')
        attach_author(book1, king)
        attach_author(book2, tolstoy)

        results = Book.search(author_ids=(king.id,))
        titles = result_titles(results)
        self.assertIn('Book by King', titles)
        self.assertNotIn('Book by Tolstoy', titles)

    def test_author_ids_or_logic(self):
        """Multiple author_ids — books of any of them are returned."""
        book1 = make_book('Book by King')
        book2 = make_book('Book by Tolstoy')
        book3 = make_book('Unrelated Book')
        king = Author.create(firstname='Стивен', lastname='Кинг')
        tolstoy = Author.create(firstname='Лев', lastname='Толстой')
        attach_author(book1, king)
        attach_author(book2, tolstoy)

        results = Book.search(author_ids=(king.id, tolstoy.id))
        titles = result_titles(results)
        self.assertIn('Book by King', titles)
        self.assertIn('Book by Tolstoy', titles)
        self.assertNotIn('Unrelated Book', titles)

    def test_author_ids_book_with_multiple_authors_matched(self):
        """Book with two authors is returned when filtering by either."""
        book = make_book('Co-authored Book')
        king = Author.create(firstname='Стивен', lastname='Кинг')
        tolstoy = Author.create(firstname='Лев', lastname='Толстой')
        attach_author(book, king)
        attach_author(book, tolstoy)

        results_king = Book.search(author_ids=(king.id,))
        self.assertIn('Co-authored Book', result_titles(results_king))

        results_tolstoy = Book.search(author_ids=(tolstoy.id,))
        self.assertIn('Co-authored Book', result_titles(results_tolstoy))

    def test_tag_ids_single(self):
        book1 = make_book('Tagged Book')
        book2 = make_book('Untagged Book')
        tag = Tag.create(name='sci-fi')
        attach_tag(book1, tag)

        results = Book.search(tag_ids=(tag.id,))
        titles = result_titles(results)
        self.assertIn('Tagged Book', titles)
        self.assertNotIn('Untagged Book', titles)

    def test_tag_ids_or_logic(self):
        book1 = make_book('Fantasy Book')
        book2 = make_book('SciFi Book')
        book3 = make_book('Other Book')
        fantasy = Tag.create(name='fantasy')
        scifi = Tag.create(name='sci-fi')
        attach_tag(book1, fantasy)
        attach_tag(book2, scifi)

        results = Book.search(tag_ids=(fantasy.id, scifi.id))
        titles = result_titles(results)
        self.assertIn('Fantasy Book', titles)
        self.assertIn('SciFi Book', titles)
        self.assertNotIn('Other Book', titles)

    def test_genre_ids_single(self):
        book1 = make_book('Horror Novel')
        book2 = make_book('Comedy Novel')
        horror = Genre.create(name='Horror')
        comedy = Genre.create(name='Comedy')
        attach_genre(book1, horror)
        attach_genre(book2, comedy)

        results = Book.search(genre_ids=(horror.id,))
        titles = result_titles(results)
        self.assertIn('Horror Novel', titles)
        self.assertNotIn('Comedy Novel', titles)

    def test_genre_ids_or_logic(self):
        book1 = make_book('Horror Novel')
        book2 = make_book('Comedy Novel')
        book3 = make_book('No Genre')
        horror = Genre.create(name='Horror')
        comedy = Genre.create(name='Comedy')
        attach_genre(book1, horror)
        attach_genre(book2, comedy)

        results = Book.search(genre_ids=(horror.id, comedy.id))
        titles = result_titles(results)
        self.assertIn('Horror Novel', titles)
        self.assertIn('Comedy Novel', titles)
        self.assertNotIn('No Genre', titles)

    def test_text_and_author_ids_combined(self):
        """text AND author_ids: only books matching both criteria."""
        book1 = make_book('Foundation')
        book2 = make_book('Dune')
        book3 = make_book('Foundation and Empire')
        asimov = Author.create(firstname='Айзек', lastname='Азимов')
        herbert = Author.create(firstname='Фрэнк', lastname='Херберт')
        attach_author(book1, asimov)
        attach_author(book2, herbert)
        attach_author(book3, asimov)

        # title contains "Foundation" AND author is Asimov
        results = Book.search(text='Foundation', author_ids=(asimov.id,))
        titles = result_titles(results)
        self.assertIn('Foundation', titles)
        self.assertIn('Foundation and Empire', titles)
        self.assertNotIn('Dune', titles)

    def test_combined_text_tag_genre(self):
        book1 = make_book('Space Opera')
        book2 = make_book('Space Western')
        tag = Tag.create(name='classic')
        genre = Genre.create(name='SciFi')
        attach_tag(book1, tag)
        attach_genre(book1, genre)
        attach_genre(book2, genre)

        # text="Space" AND tag=classic → only book1
        results = Book.search(text='Space', tag_ids=(tag.id,))
        titles = result_titles(results)
        self.assertIn('Space Opera', titles)
        self.assertNotIn('Space Western', titles)

    def test_empty_author_ids_no_filter(self):
        """Empty author_ids tuple means no author filter is applied."""
        make_book('Book A')
        make_book('Book B')
        results = Book.search(author_ids=())
        self.assertEqual(len(list(results)), 2)

    def test_empty_tag_ids_no_filter(self):
        make_book('Book A')
        results = Book.search(tag_ids=())
        self.assertEqual(len(list(results)), 1)

    def test_empty_genre_ids_no_filter(self):
        make_book('Book A')
        results = Book.search(genre_ids=())
        self.assertEqual(len(list(results)), 1)


# ── TestBookSearchOrder ────────────────────────────────────────────────────────

class TestBookSearchOrder(BaseTestCase):

    def test_results_ordered_by_title_alphabetically(self):
        make_book('Zebra')
        make_book('Apple')
        make_book('Mango')

        titles = result_titles(Book.search())
        self.assertEqual(titles, ['Apple', 'Mango', 'Zebra'])

    def test_results_ordered_case_insensitive(self):
        make_book('zebra')
        make_book('Apple')
        make_book('mango')

        titles = result_titles(Book.search())
        self.assertEqual(titles, ['Apple', 'mango', 'zebra'])

    def test_search_results_ordered(self):
        make_book('Zeta Book')
        make_book('Alpha Book')
        make_book('Gamma Book')

        results = Book.search(text='Book')
        titles = result_titles(results)
        self.assertEqual(titles, ['Alpha Book', 'Gamma Book', 'Zeta Book'])


if __name__ == '__main__':
    unittest.main()
