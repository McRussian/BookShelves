import unittest

from src.database.models.author import Author, AuthorAlias
from src.gui.authors.author_list_widget import build_author_results
from tests.database.conftest import BaseTestCase


class TestBuildAuthorResults(BaseTestCase):
    """build_author_results — поиск по БД + preselected_cache всегда в результатах."""

    # ── базовый поиск ─────────────────────────────────────────────────────────

    def test_matched_author_appears(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('Кинг', {})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].lastname, 'Кинг')

    def test_no_match_empty_cache_returns_empty(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('Толстой', {})
        self.assertEqual(results, [])

    def test_partial_match(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('Кин', {})
        self.assertEqual(len(results), 1)

    def test_search_by_alias(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        results = build_author_results('Бахман', {})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, author.id)

    # ── preselected_cache ─────────────────────────────────────────────────────

    def test_preselected_appears_even_if_not_matched(self):
        king = Author.create(firstname='Стивен', lastname='Кинг')
        dostoevsky = Author.create(firstname='Фёдор', lastname='Достоевский')
        results = build_author_results('Достоевский', {king.id: king})
        ids = [a.id for a in results]
        self.assertIn(king.id, ids)
        self.assertIn(dostoevsky.id, ids)

    def test_preselected_comes_first(self):
        king = Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        results = build_author_results('Достоевский', {king.id: king})
        self.assertEqual(results[0].id, king.id)

    def test_preselected_not_duplicated_when_also_matched(self):
        king = Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('Кинг', {king.id: king})
        self.assertEqual(len(results), 1)

    def test_multiple_preselected_all_appear(self):
        king = Author.create(firstname='Стивен', lastname='Кинг')
        dostoevsky = Author.create(firstname='Фёдор', lastname='Достоевский')
        tolstoy = Author.create(firstname='Лев', lastname='Толстой')
        results = build_author_results('Толстой', {king.id: king, dostoevsky.id: dostoevsky})
        ids = [a.id for a in results]
        self.assertIn(king.id, ids)
        self.assertIn(dostoevsky.id, ids)
        self.assertIn(tolstoy.id, ids)

    def test_no_preselected_returns_only_matched(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        results = build_author_results('Кинг', {})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].lastname, 'Кинг')

    def test_empty_cache_and_no_match_returns_empty(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('xyz', {})
        self.assertEqual(results, [])

    def test_only_preselected_no_db_match(self):
        king = Author.create(firstname='Стивен', lastname='Кинг')
        results = build_author_results('xyz', {king.id: king})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, king.id)

    # ── автор без фамилии ─────────────────────────────────────────────────────

    def test_search_author_without_lastname(self):
        Author.create(firstname='Гомер')
        results = build_author_results('Гомер', {})
        self.assertEqual(len(results), 1)

    def test_null_lastname_does_not_crash(self):
        Author.create(firstname='Гомер')
        results = build_author_results('Кинг', {})
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
