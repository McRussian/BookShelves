"""Тесты справочников: Genre, Tag, BookFormat, Edition, Publisher."""
import unittest
from peewee import IntegrityError

from src.database.models.book_format import BookFormat
from src.database.models.edition import Edition
from src.database.models.genre import Genre
from src.database.models.publisher import Publisher
from src.database.models.tag import Tag
from tests.database.conftest import BaseTestCase


class TestGenre(BaseTestCase):

    def test_create(self):
        genre = Genre.create(name='Фантастика')
        self.assertEqual(Genre.get_by_id(genre.id).name, 'Фантастика')

    def test_without_parent(self):
        genre = Genre.create(name='Фантастика')
        self.assertIsNone(genre.parent_id)

    def test_hierarchy(self):
        parent = Genre.create(name='Фантастика')
        child = Genre.create(name='Космическая опера', parent=parent)
        self.assertEqual(Genre.get_by_id(child.id).parent_id, parent.id)

    def test_children_backref(self):
        parent = Genre.create(name='Фантастика')
        Genre.create(name='Космическая опера', parent=parent)
        Genre.create(name='Киберпанк', parent=parent)
        self.assertEqual(parent.children.count(), 2)

    def test_multiple_levels(self):
        root = Genre.create(name='Художественная литература')
        mid = Genre.create(name='Фантастика', parent=root)
        leaf = Genre.create(name='Киберпанк', parent=mid)
        self.assertEqual(leaf.parent_id, mid.id)
        self.assertEqual(mid.parent_id, root.id)

    def test_parent_set_null_on_delete(self):
        parent = Genre.create(name='Фантастика')
        child = Genre.create(name='Киберпанк', parent=parent)
        parent.delete_instance()
        reloaded = Genre.get_by_id(child.id)
        self.assertIsNone(reloaded.parent_id)

    def test_unique_name(self):
        Genre.create(name='Фантастика')
        with self.assertRaises(IntegrityError):
            Genre.create(name='Фантастика')

    def test_delete(self):
        genre = Genre.create(name='Фантастика')
        genre.delete_instance()
        self.assertEqual(Genre.select().count(), 0)


class TestTag(BaseTestCase):

    def test_create(self):
        tag = Tag.create(name='python')
        self.assertEqual(Tag.get_by_id(tag.id).name, 'python')

    def test_unique_name(self):
        Tag.create(name='python')
        with self.assertRaises(IntegrityError):
            Tag.create(name='python')

    def test_create_multiple(self):
        Tag.create(name='python')
        Tag.create(name='алгоритмы')
        self.assertEqual(Tag.select().count(), 2)

    def test_delete(self):
        tag = Tag.create(name='python')
        tag.delete_instance()
        self.assertEqual(Tag.select().count(), 0)


class TestBookFormat(BaseTestCase):

    def test_create(self):
        fmt = BookFormat.create(name='epub')
        self.assertEqual(BookFormat.get_by_id(fmt.id).name, 'epub')

    def test_unique_name(self):
        BookFormat.create(name='epub')
        with self.assertRaises(IntegrityError):
            BookFormat.create(name='epub')

    def test_create_multiple(self):
        BookFormat.create(name='epub')
        BookFormat.create(name='pdf')
        BookFormat.create(name='fb2')
        self.assertEqual(BookFormat.select().count(), 3)


class TestEdition(BaseTestCase):

    def test_create(self):
        ed = Edition.create(name='Первое издание')
        self.assertEqual(Edition.get_by_id(ed.id).name, 'Первое издание')

    def test_unique_name(self):
        Edition.create(name='Первое издание')
        with self.assertRaises(IntegrityError):
            Edition.create(name='Первое издание')


class TestPublisher(BaseTestCase):

    def test_create_with_comment(self):
        pub = Publisher.create(name='АСТ', comment='Крупное российское издательство')
        saved = Publisher.get_by_id(pub.id)
        self.assertEqual(saved.name, 'АСТ')
        self.assertEqual(saved.comment, 'Крупное российское издательство')

    def test_create_without_comment(self):
        pub = Publisher.create(name='Эксмо')
        self.assertIsNone(pub.comment)

    def test_create_multiple(self):
        Publisher.create(name='АСТ')
        Publisher.create(name='Эксмо')
        self.assertEqual(Publisher.select().count(), 2)

    def test_delete(self):
        pub = Publisher.create(name='АСТ')
        pub.delete_instance()
        self.assertEqual(Publisher.select().count(), 0)


if __name__ == '__main__':
    unittest.main()
