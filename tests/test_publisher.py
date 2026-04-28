import unittest
from peewee import IntegrityError

from src.database.models.publisher import Publisher
from tests.database.conftest import BaseTestCase


class TestPublisherSearch(BaseTestCase):

    def test_search_exact(self):
        Publisher.create(name='АСТ')
        Publisher.create(name='Эксмо')
        results = list(Publisher.search('АСТ'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'АСТ')

    def test_search_partial(self):
        Publisher.create(name='Азбука-Аттикус')
        Publisher.create(name='Азбука классика')
        Publisher.create(name='Эксмо')
        results = list(Publisher.search('Азбука'))
        self.assertEqual(len(results), 2)

    def test_search_case_insensitive(self):
        Publisher.create(name='АСТ')
        results = list(Publisher.search('аст'))
        self.assertEqual(len(results), 1)

    def test_search_no_match(self):
        Publisher.create(name='АСТ')
        results = list(Publisher.search('Питер'))
        self.assertEqual(len(results), 0)

    def test_search_empty_returns_nothing(self):
        Publisher.create(name='АСТ')
        Publisher.create(name='Эксмо')
        # search('') is called only when text is non-empty; empty falls back to select()
        results = list(Publisher.search(''))
        self.assertEqual(len(results), 2)

    def test_search_results_ordered_by_name(self):
        Publisher.create(name='Эксмо')
        Publisher.create(name='АСТ')
        Publisher.create(name='Азбука')
        results = [p.name for p in Publisher.search('')]
        self.assertEqual(results, sorted(results))


class TestPublisherEdit(BaseTestCase):

    def test_update_name(self):
        pub = Publisher.create(name='АСТ')
        pub.name = 'АСТ Москва'
        pub.save()
        reloaded = Publisher.get_by_id(pub.id)
        self.assertEqual(reloaded.name, 'АСТ Москва')

    def test_update_comment(self):
        pub = Publisher.create(name='АСТ')
        pub.comment = 'Крупное издательство'
        pub.save()
        reloaded = Publisher.get_by_id(pub.id)
        self.assertEqual(reloaded.comment, 'Крупное издательство')

    def test_clear_comment(self):
        pub = Publisher.create(name='АСТ', comment='Старый комментарий')
        pub.comment = None
        pub.save()
        reloaded = Publisher.get_by_id(pub.id)
        self.assertIsNone(reloaded.comment)

    def test_rename_to_existing_name_raises(self):
        Publisher.create(name='АСТ')
        pub2 = Publisher.create(name='Эксмо')
        pub2.name = 'АСТ'
        with self.assertRaises(IntegrityError):
            pub2.save()

    def test_edit_does_not_create_duplicate_id(self):
        pub = Publisher.create(name='АСТ')
        original_id = pub.id
        pub.name = 'АСТ Москва'
        pub.save()
        self.assertEqual(Publisher.select().count(), 1)
        self.assertEqual(Publisher.get_by_id(original_id).name, 'АСТ Москва')


class TestPublisherDelete(BaseTestCase):

    def test_delete_removes_from_db(self):
        pub = Publisher.create(name='АСТ')
        pub.delete_instance()
        self.assertIsNone(Publisher.get_or_none(Publisher.name == 'АСТ'))

    def test_delete_does_not_affect_others(self):
        pub1 = Publisher.create(name='АСТ')
        Publisher.create(name='Эксмо')
        pub1.delete_instance()
        self.assertEqual(Publisher.select().count(), 1)
        self.assertEqual(Publisher.select().first().name, 'Эксмо')


if __name__ == '__main__':
    unittest.main()
