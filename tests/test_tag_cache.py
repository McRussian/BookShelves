import unittest
from types import SimpleNamespace

from peewee import SqliteDatabase

from src.database.database import database_proxy
from src.database.models.tag import Tag
from src.gui.dialogs.tag_search_dialog import build_search_results, filter_tags


def _tag(name: str, tag_id: int = 0) -> SimpleNamespace:
    return SimpleNamespace(name=name, id=tag_id)


class TestFilterTags(unittest.TestCase):
    """filter_tags — чистая Python-функция, БД не нужна."""

    def test_empty_query_returns_all(self):
        tags = [_tag('#Фэнтези'), _tag('#Детектив')]
        self.assertEqual(filter_tags(tags, ''), tags)

    def test_empty_list(self):
        self.assertEqual(filter_tags([], 'фэнтези'), [])

    def test_cyrillic_case_insensitive(self):
        tags = [_tag('#Фэнтези'), _tag('#Детектив')]
        self.assertEqual(filter_tags(tags, 'фэн'), [tags[0]])

    def test_cyrillic_uppercase_query(self):
        tags = [_tag('#Фэнтези'), _tag('#Детектив')]
        self.assertEqual(filter_tags(tags, 'ФЭН'), [tags[0]])

    def test_latin_case_insensitive(self):
        tags = [_tag('#SciFi'), _tag('#Fantasy')]
        self.assertEqual(filter_tags(tags, 'scifi'), [tags[0]])

    def test_no_match_returns_empty(self):
        self.assertEqual(filter_tags([_tag('#Фэнтези')], 'детектив'), [])

    def test_substring_match_multiple(self):
        tags = [_tag('#НаучнаяФантастика'), _tag('#Фантастика'), _tag('#Детектив')]
        self.assertEqual(len(filter_tags(tags, 'фантастика')), 2)

    def test_hash_in_query(self):
        tags = [_tag('#Фэнтези'), _tag('#Детектив')]
        self.assertEqual(filter_tags(tags, '#фэн'), [tags[0]])

    def test_query_matches_all(self):
        tags = [_tag('#АБВ'), _tag('#АГД')]
        self.assertEqual(filter_tags(tags, '#а'), tags)

    def test_order_preserved(self):
        tags = [_tag('#Б'), _tag('#А'), _tag('#В')]
        self.assertEqual(filter_tags(tags, '#'), tags)


class TestBuildSearchResults(unittest.TestCase):
    """build_search_results — отмеченные теги всегда в результатах поиска."""

    def test_matched_tag_appears(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, set(), 'фэн')
        self.assertEqual(result, [tags[0]])

    def test_checked_tag_appears_even_if_not_matched(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, {1}, 'дет')
        self.assertIn(tags[0], result)
        self.assertIn(tags[1], result)

    def test_checked_tag_comes_first(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, {1}, 'дет')
        self.assertEqual(result[0], tags[0])

    def test_checked_and_matched_not_duplicated(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, {1}, 'фэн')
        self.assertEqual(result.count(tags[0]), 1)

    def test_no_selection_returns_only_matched(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, set(), 'фэн')
        self.assertEqual(result, [tags[0]])

    def test_multiple_checked_all_appear(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2), _tag('#Триллер', 3)]
        result = build_search_results(tags, {1, 2}, 'триллер')
        self.assertEqual(len(result), 3)

    def test_no_match_no_selection_empty(self):
        tags = [_tag('#Фэнтези', 1)]
        result = build_search_results(tags, set(), 'детектив')
        self.assertEqual(result, [])

    def test_no_match_but_checked_returns_checked(self):
        tags = [_tag('#Фэнтези', 1), _tag('#Детектив', 2)]
        result = build_search_results(tags, {1}, 'xyz')
        self.assertEqual(result, [tags[0]])


class TestTagCacheOperations(unittest.TestCase):
    """Операции синхронизации кеша с базой данных."""

    def setUp(self):
        db = SqliteDatabase(':memory:')
        db.connect()
        database_proxy.initialize(db)
        db.create_tables([Tag])

    def tearDown(self):
        db = database_proxy.obj
        db.drop_tables([Tag])
        db.close()

    def _load_cache(self) -> list[Tag]:
        return list(Tag.select().order_by(Tag.name))

    # ── начальная загрузка ────────────────────────────────────────────────────

    def test_initial_load_sorted(self):
        Tag.create(name='#Фэнтези')
        Tag.create(name='#Детектив')
        cache = self._load_cache()
        self.assertEqual([t.name for t in cache], ['#Детектив', '#Фэнтези'])

    def test_initial_load_empty_db(self):
        self.assertEqual(self._load_cache(), [])

    # ── добавление тега ───────────────────────────────────────────────────────

    def test_add_tag_appears_in_cache(self):
        cache = self._load_cache()
        new_tag = Tag.create(name='#Фэнтези')
        cache.append(new_tag)
        cache.sort(key=lambda t: t.name)
        self.assertIn(new_tag, cache)

    def test_add_tag_sorted_correctly(self):
        Tag.create(name='#Фэнтези')
        cache = self._load_cache()
        new_tag = Tag.create(name='#Детектив')
        cache.append(new_tag)
        cache.sort(key=lambda t: t.name)
        self.assertEqual([t.name for t in cache], ['#Детектив', '#Фэнтези'])

    def test_added_tag_filterable_immediately(self):
        cache = self._load_cache()
        new_tag = Tag.create(name='#Фэнтези')
        cache.append(new_tag)
        cache.sort(key=lambda t: t.name)
        self.assertEqual(filter_tags(cache, 'фэн'), [new_tag])

    def test_added_tag_not_returned_for_unrelated_query(self):
        cache = self._load_cache()
        new_tag = Tag.create(name='#Фэнтези')
        cache.append(new_tag)
        cache.sort(key=lambda t: t.name)
        self.assertEqual(filter_tags(cache, 'детектив'), [])

    # ── удаление тега ─────────────────────────────────────────────────────────

    def test_delete_tag_removed_from_cache(self):
        t1 = Tag.create(name='#Фэнтези')
        t2 = Tag.create(name='#Детектив')
        cache = [t1, t2]
        deleted_ids = {t1.id}
        t1.delete_instance()
        cache = [t for t in cache if t.id not in deleted_ids]
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache[0].name, '#Детектив')

    def test_deleted_tag_not_in_filter_results(self):
        t1 = Tag.create(name='#Фэнтези')
        t2 = Tag.create(name='#Детектив')
        cache = [t1, t2]
        deleted_ids = {t1.id}
        t1.delete_instance()
        cache = [t for t in cache if t.id not in deleted_ids]
        self.assertEqual(filter_tags(cache, 'фэн'), [])

    def test_delete_multiple_tags(self):
        t1 = Tag.create(name='#Фэнтези')
        t2 = Tag.create(name='#Детектив')
        t3 = Tag.create(name='#Триллер')
        cache = [t1, t2, t3]
        deleted_ids = {t1.id, t2.id}
        for t in [t1, t2]:
            t.delete_instance()
        cache = [t for t in cache if t.id not in deleted_ids]
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache[0].name, '#Триллер')

    def test_delete_nonexistent_id_is_safe(self):
        t1 = Tag.create(name='#Фэнтези')
        cache = [t1]
        cache = [t for t in cache if t.id not in {9999}]
        self.assertEqual(len(cache), 1)

    def test_delete_removes_from_db(self):
        tag = Tag.create(name='#Фэнтези')
        tag.delete_instance()
        self.assertIsNone(Tag.get_or_none(Tag.name == '#Фэнтези'))

    def test_delete_multiple_removes_all_from_db(self):
        t1 = Tag.create(name='#Фэнтези')
        t2 = Tag.create(name='#Детектив')
        t1.delete_instance()
        t2.delete_instance()
        self.assertEqual(Tag.select().count(), 0)

    def test_delete_all_tags_cache_and_filter_empty(self):
        t1 = Tag.create(name='#Фэнтези')
        t2 = Tag.create(name='#Детектив')
        cache = [t1, t2]
        deleted_ids = {t.id for t in cache}
        for t in cache:
            t.delete_instance()
        cache = [t for t in cache if t.id not in deleted_ids]
        self.assertEqual(cache, [])
        self.assertEqual(filter_tags(cache, ''), [])

    def test_reload_after_delete_reflects_db(self):
        t1 = Tag.create(name='#Фэнтези')
        Tag.create(name='#Детектив')
        t1.delete_instance()
        reloaded = self._load_cache()
        self.assertEqual([t.name for t in reloaded], ['#Детектив'])


if __name__ == '__main__':
    unittest.main()
