import unittest
from peewee import IntegrityError

from src.database.models.shelf import Shelf
from src.database.models.user import User
from tests.database.conftest import BaseTestCase


class TestShelfCreate(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')

    def test_create_shelf(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        self.assertEqual(shelf.name, 'Sci-Fi')
        self.assertEqual(shelf.user_id, self.user.id)
        self.assertEqual(Shelf.select().count(), 1)

    def test_create_multiple_shelves(self):
        Shelf.create(name='Sci-Fi', user=self.user)
        Shelf.create(name='Фэнтези', user=self.user)
        self.assertEqual(Shelf.select().count(), 2)

    def test_duplicate_name_same_user_raises(self):
        Shelf.create(name='Sci-Fi', user=self.user)
        with self.assertRaises(IntegrityError):
            Shelf.create(name='Sci-Fi', user=self.user)

    def test_same_name_different_users_ok(self):
        user2 = User.create(login='bob', firstname='Bob')
        Shelf.create(name='Sci-Fi', user=self.user)
        shelf2 = Shelf.create(name='Sci-Fi', user=user2)
        self.assertIsNotNone(shelf2.id)


class TestShelfDelete(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')

    def test_delete_shelf(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        shelf.delete_instance()
        self.assertIsNone(Shelf.get_or_none(Shelf.id == shelf.id))

    def test_delete_one_of_many(self):
        s1 = Shelf.create(name='Sci-Fi', user=self.user)
        s2 = Shelf.create(name='Фэнтези', user=self.user)
        s1.delete_instance()
        self.assertIsNone(Shelf.get_or_none(Shelf.id == s1.id))
        self.assertIsNotNone(Shelf.get_or_none(Shelf.id == s2.id))

    def test_delete_user_cascades_shelves(self):
        Shelf.create(name='Sci-Fi', user=self.user)
        Shelf.create(name='Фэнтези', user=self.user)
        self.user.delete_instance()
        self.assertEqual(Shelf.select().count(), 0)


class TestShelfRename(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')

    def test_rename_shelf(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        shelf.name = 'Hard SF'
        shelf.save()
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertEqual(reloaded.name, 'Hard SF')

    def test_rename_to_existing_name_raises(self):
        Shelf.create(name='Sci-Fi', user=self.user)
        shelf2 = Shelf.create(name='Фэнтezi', user=self.user)
        shelf2.name = 'Sci-Fi'
        with self.assertRaises(IntegrityError):
            shelf2.save()


class TestShelfForUser(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')
        self.user2 = User.create(login='bob', firstname='Bob')

    def test_for_user_returns_only_own_shelves(self):
        Shelf.create(name='Sci-Fi', user=self.user)
        Shelf.create(name='Чужая', user=self.user2)
        shelves = Shelf.for_user(self.user)
        self.assertEqual(len(shelves), 1)
        self.assertEqual(shelves[0].name, 'Sci-Fi')

    def test_for_user_ordered_by_name(self):
        Shelf.create(name='Фэнтези', user=self.user)
        Shelf.create(name='Sci-Fi', user=self.user)
        Shelf.create(name='Детектив', user=self.user)
        names = [s.name for s in Shelf.for_user(self.user)]
        self.assertEqual(names, sorted(names, key=str.lower))

    def test_for_user_empty(self):
        self.assertEqual(Shelf.for_user(self.user), [])


class TestShelfIsActive(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')

    def test_default_is_active(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        self.assertTrue(shelf.is_active)

    def test_create_inactive(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user, is_active=False)
        self.assertFalse(shelf.is_active)

    def test_toggle_to_inactive(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        shelf.is_active = False
        shelf.save()
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertFalse(reloaded.is_active)

    def test_toggle_back_to_active(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user, is_active=False)
        shelf.is_active = True
        shelf.save()
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertTrue(reloaded.is_active)

    def test_for_user_returns_all_regardless_of_active(self):
        Shelf.create(name='Активная', user=self.user, is_active=True)
        Shelf.create(name='Неактивная', user=self.user, is_active=False)
        self.assertEqual(len(Shelf.for_user(self.user)), 2)


class TestShelfDescription(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = User.create(login='alice', firstname='Alice')

    def test_default_description_is_none(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        self.assertIsNone(shelf.description)

    def test_create_with_description(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user, description='Твёрдая НФ')
        self.assertEqual(shelf.description, 'Твёрдая НФ')

    def test_set_description(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user)
        shelf.description = 'Подборка для поездок'
        shelf.save()
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertEqual(reloaded.description, 'Подборка для поездок')

    def test_clear_description(self):
        shelf = Shelf.create(name='Sci-Fi', user=self.user, description='Что-то')
        shelf.description = None
        shelf.save()
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertIsNone(reloaded.description)

    def test_description_multiline(self):
        text = 'Строка 1\nСтрока 2\nСтрока 3'
        shelf = Shelf.create(name='Sci-Fi', user=self.user, description=text)
        reloaded = Shelf.get_by_id(shelf.id)
        self.assertEqual(reloaded.description, text)


if __name__ == '__main__':
    unittest.main()
