import unittest

from src.database.models.book import Book
from src.database.models.shelf import Shelf, ShelfBook
from src.database.models.user import User
from tests.database.conftest import BaseTestCase


class TestShelfBook(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')
        self.shelf = Shelf.create(name='Sci-Fi', user=self.user)
        self.b1 = Book.create(title='Дюна', file_path='/books/dune.epub')
        self.b2 = Book.create(title='Основание', file_path='/books/foundation.epub')
        self.b3 = Book.create(title='Солярис', file_path='/books/solaris.epub')

    # ── add_book ──────────────────────────────────────────────────────────────

    def test_add_book(self):
        self.shelf.add_book(self.b1)
        self.assertEqual(ShelfBook.select().count(), 1)

    def test_add_book_returns_shelf_book(self):
        sb = self.shelf.add_book(self.b1)
        self.assertEqual(sb.book_id, self.b1.id)
        self.assertEqual(sb.shelf_id, self.shelf.id)

    def test_add_book_duplicate_is_idempotent(self):
        self.shelf.add_book(self.b1)
        self.shelf.add_book(self.b1)
        self.assertEqual(ShelfBook.select().count(), 1)

    def test_add_multiple_books_increments_position(self):
        sb1 = self.shelf.add_book(self.b1)
        sb2 = self.shelf.add_book(self.b2)
        sb3 = self.shelf.add_book(self.b3)
        self.assertLess(sb1.position, sb2.position)
        self.assertLess(sb2.position, sb3.position)

    def test_add_book_to_different_shelves(self):
        shelf2 = Shelf.create(name='Фэнтези', user=self.user)
        self.shelf.add_book(self.b1)
        shelf2.add_book(self.b1)
        self.assertEqual(ShelfBook.select().count(), 2)

    # ── get_books ─────────────────────────────────────────────────────────────

    def test_get_books_empty(self):
        self.assertEqual(self.shelf.get_books(), [])

    def test_get_books_returns_added(self):
        self.shelf.add_book(self.b1)
        self.shelf.add_book(self.b2)
        books = self.shelf.get_books()
        self.assertEqual(len(books), 2)

    def test_get_books_ordered_by_position(self):
        self.shelf.add_book(self.b1)
        self.shelf.add_book(self.b2)
        self.shelf.add_book(self.b3)
        books = self.shelf.get_books()
        self.assertEqual([b.id for b in books], [self.b1.id, self.b2.id, self.b3.id])

    def test_get_books_isolated_between_shelves(self):
        shelf2 = Shelf.create(name='Фэнтези', user=self.user)
        self.shelf.add_book(self.b1)
        shelf2.add_book(self.b2)
        self.assertEqual([b.id for b in self.shelf.get_books()], [self.b1.id])
        self.assertEqual([b.id for b in shelf2.get_books()], [self.b2.id])

    # ── remove_book ───────────────────────────────────────────────────────────

    def test_remove_book(self):
        self.shelf.add_book(self.b1)
        self.shelf.remove_book(self.b1)
        self.assertEqual(self.shelf.get_books(), [])

    def test_remove_book_leaves_others(self):
        self.shelf.add_book(self.b1)
        self.shelf.add_book(self.b2)
        self.shelf.remove_book(self.b1)
        self.assertEqual([b.id for b in self.shelf.get_books()], [self.b2.id])

    def test_remove_book_from_one_shelf_leaves_other_shelf(self):
        shelf2 = Shelf.create(name='Фэнтези', user=self.user)
        self.shelf.add_book(self.b1)
        shelf2.add_book(self.b1)
        self.shelf.remove_book(self.b1)
        self.assertEqual(self.shelf.get_books(), [])
        self.assertEqual([b.id for b in shelf2.get_books()], [self.b1.id])

    def test_remove_book_not_on_shelf_is_safe(self):
        self.shelf.add_book(self.b1)
        self.shelf.remove_book(self.b2)
        self.assertEqual(len(self.shelf.get_books()), 1)

    # ── каскадное удаление ────────────────────────────────────────────────────

    def test_delete_shelf_cascades_shelf_books(self):
        self.shelf.add_book(self.b1)
        self.shelf.delete_instance()
        self.assertEqual(ShelfBook.select().count(), 0)

    def test_delete_book_cascades_shelf_books(self):
        self.shelf.add_book(self.b1)
        self.b1.delete_instance()
        self.assertEqual(ShelfBook.select().count(), 0)

    def test_delete_book_cascades_only_its_own_shelf_books(self):
        shelf2 = Shelf.create(name='Фэнтези', user=self.user)
        self.shelf.add_book(self.b1)
        self.shelf.add_book(self.b2)
        shelf2.add_book(self.b1)
        self.b1.delete_instance()
        self.assertEqual(ShelfBook.select().count(), 1)
        self.assertEqual(self.shelf.get_books()[0].id, self.b2.id)


if __name__ == '__main__':
    unittest.main()
