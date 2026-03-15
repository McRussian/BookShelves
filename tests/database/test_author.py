import unittest

from src.database.models.author import Author, AuthorAlias
from tests.database.conftest import BaseTestCase


class TestAuthorCreate(BaseTestCase):

    def test_create_full(self):
        author = Author.create(firstname='Стивен', lastname='Кинг', comment='Мастер ужасов')
        saved = Author.get_by_id(author.id)
        self.assertEqual(saved.firstname, 'Стивен')
        self.assertEqual(saved.lastname, 'Кинг')
        self.assertEqual(saved.comment, 'Мастер ужасов')

    def test_create_minimal(self):
        author = Author.create(firstname='Гомер')
        saved = Author.get_by_id(author.id)
        self.assertEqual(saved.firstname, 'Гомер')
        self.assertIsNone(saved.lastname)
        self.assertIsNone(saved.surname)

    def test_create_multiple(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        self.assertEqual(Author.select().count(), 2)


class TestAuthorFullName(BaseTestCase):

    def test_lastname_firstname(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        self.assertEqual(author.full_name, 'Кинг Стивен')

    def test_with_surname(self):
        author = Author.create(firstname='Александр', lastname='Пушкин', surname='Сергеевич')
        self.assertEqual(author.full_name, 'Пушкин Александр Сергеевич')

    def test_only_firstname(self):
        author = Author.create(firstname='Гомер')
        self.assertEqual(author.full_name, 'Гомер')


class TestAuthorAliases(BaseTestCase):

    def test_aliases_str_empty(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        self.assertEqual(author.aliases_str, '')

    def test_aliases_str_single(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        self.assertEqual(author.aliases_str, 'Ричард Бахман')

    def test_aliases_str_multiple(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        AuthorAlias.create(author=author, alias='Джон Свиффен')
        result = author.aliases_str
        self.assertIn('Ричард Бахман', result)
        self.assertIn('Джон Свиффен', result)

    def test_display_name_without_aliases(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        self.assertEqual(author.display_name, 'Кинг Стивен')

    def test_display_name_with_alias(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        self.assertEqual(author.display_name, 'Кинг Стивен (Ричард Бахман)')

    def test_display_name_by_alias_without_aliases(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        self.assertEqual(author.display_name_by_alias, 'Кинг Стивен')

    def test_display_name_by_alias_with_alias(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        self.assertEqual(author.display_name_by_alias, 'Ричард Бахман (Кинг Стивен)')


class TestAuthorDelete(BaseTestCase):

    def test_delete_author(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        author.delete_instance()
        self.assertEqual(Author.select().count(), 0)

    def test_delete_cascades_to_aliases(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        AuthorAlias.create(author=author, alias='Джон Свиффен')
        self.assertEqual(AuthorAlias.select().count(), 2)
        author.delete_instance()
        self.assertEqual(AuthorAlias.select().count(), 0)

    def test_delete_alias_keeps_author(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        alias = AuthorAlias.create(author=author, alias='Ричард Бахман')
        alias.delete_instance()
        self.assertEqual(Author.select().count(), 1)
        self.assertEqual(AuthorAlias.select().count(), 0)


class TestAuthorSearch(BaseTestCase):

    def test_search_by_lastname(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        results = list(Author.search('Кинг'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].lastname, 'Кинг')

    def test_search_by_firstname(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        results = list(Author.search('Стивен'))
        self.assertEqual(len(results), 1)

    def test_search_by_surname(self):
        Author.create(firstname='Александр', lastname='Пушкин', surname='Сергеевич')
        results = list(Author.search('Сергеевич'))
        self.assertEqual(len(results), 1)

    def test_search_by_alias(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        results = list(Author.search('Бахман'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, author.id)

    def test_search_no_duplicates_multiple_aliases(self):
        author = Author.create(firstname='Стивен', lastname='Кинг')
        AuthorAlias.create(author=author, alias='Ричард Бахман')
        AuthorAlias.create(author=author, alias='Ричард Смит')
        results = list(Author.search('Ричард'))
        self.assertEqual(len(results), 1)

    def test_search_partial_match(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = list(Author.search('Кин'))
        self.assertEqual(len(results), 1)

    def test_search_not_found(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        results = list(Author.search('Толстой'))
        self.assertEqual(len(results), 0)

    def test_search_empty_returns_all(self):
        Author.create(firstname='Стивен', lastname='Кинг')
        Author.create(firstname='Фёдор', lastname='Достоевский')
        results = list(Author.search(''))
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main()
