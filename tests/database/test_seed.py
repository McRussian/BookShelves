"""Тесты заполнения справочников: Edition и Genre (seed)."""
import unittest

from src.database.models.edition import Edition
from src.database.models.genre import Genre
from src.database.seed import _seed_genres, seed_reference_data
from tests.database.conftest import BaseTestCase


# ---------------------------------------------------------------------------
# Вспомогательная функция: строим дерево из БД для проверки
# ---------------------------------------------------------------------------

def _build_db_tree(parent_id=None) -> list:
    """Возвращает список (name, [children]) для узлов с данным parent_id."""
    nodes = Genre.select().where(Genre.parent == parent_id)
    return [(g.name, _build_db_tree(g.id)) for g in nodes]


# ---------------------------------------------------------------------------
# Тест-дерево фиксированной структуры глубиной до 7 уровней
# ---------------------------------------------------------------------------

TEST_TREE = [
    ('L1-A', [
        ('L2-A1', [
            ('L3-A1a', [
                ('L4-A1a-i', [
                    ('L5-A1a-i-alpha', [
                        ('L6-A1a-i-alpha-1', [
                            ('L7-leaf', []),
                        ]),
                    ]),
                ]),
                ('L4-A1a-ii', []),
            ]),
            ('L3-A1b', []),
        ]),
        ('L2-A2', [
            ('L3-A2a', []),
            ('L3-A2b', [
                ('L4-A2b-i', []),
            ]),
        ]),
    ]),
    ('L1-B', [
        ('L2-B1', []),
        ('L2-B2', [
            ('L3-B2a', [
                ('L4-B2a-i', [
                    ('L5-B2a-i-alpha', []),
                    ('L5-B2a-i-beta', []),
                ]),
            ]),
        ]),
    ]),
    ('L1-C', []),
]

# Имена всех узлов тестового дерева (для подсчёта)
_ALL_NAMES = [
    'L1-A', 'L2-A1', 'L3-A1a', 'L4-A1a-i', 'L5-A1a-i-alpha',
    'L6-A1a-i-alpha-1', 'L7-leaf', 'L4-A1a-ii', 'L3-A1b',
    'L2-A2', 'L3-A2a', 'L3-A2b', 'L4-A2b-i',
    'L1-B', 'L2-B1', 'L2-B2', 'L3-B2a', 'L4-B2a-i',
    'L5-B2a-i-alpha', 'L5-B2a-i-beta',
    'L1-C',
]


class TestSeedGenresCount(BaseTestCase):

    def setUp(self):
        super().setUp()
        _seed_genres(TEST_TREE, parent=None)

    def test_total_count(self):
        self.assertEqual(Genre.select().count(), len(_ALL_NAMES))

    def test_all_names_present(self):
        saved = {g.name for g in Genre.select()}
        self.assertEqual(saved, set(_ALL_NAMES))

    def test_root_count(self):
        roots = Genre.select().where(Genre.parent.is_null())
        self.assertEqual(roots.count(), 3)  # L1-A, L1-B, L1-C


class TestSeedGenresParentLinks(BaseTestCase):

    def setUp(self):
        super().setUp()
        _seed_genres(TEST_TREE, parent=None)

    def _get(self, name: str) -> Genre:
        return Genre.get(Genre.name == name)

    def test_level1_has_no_parent(self):
        for name in ('L1-A', 'L1-B', 'L1-C'):
            self.assertIsNone(self._get(name).parent_id, name)

    def test_level2_parent_is_level1(self):
        self.assertEqual(self._get('L2-A1').parent_id, self._get('L1-A').id)
        self.assertEqual(self._get('L2-A2').parent_id, self._get('L1-A').id)
        self.assertEqual(self._get('L2-B1').parent_id, self._get('L1-B').id)
        self.assertEqual(self._get('L2-B2').parent_id, self._get('L1-B').id)

    def test_deep_chain(self):
        """L1-A → L2-A1 → L3-A1a → L4-A1a-i → L5… → L6… → L7-leaf."""
        chain = ['L1-A', 'L2-A1', 'L3-A1a', 'L4-A1a-i',
                 'L5-A1a-i-alpha', 'L6-A1a-i-alpha-1', 'L7-leaf']
        for parent_name, child_name in zip(chain, chain[1:]):
            self.assertEqual(
                self._get(child_name).parent_id,
                self._get(parent_name).id,
                f'{child_name} → parent should be {parent_name}',
            )

    def test_leaf_has_no_children(self):
        self.assertEqual(self._get('L7-leaf').children.count(), 0)
        self.assertEqual(self._get('L1-C').children.count(), 0)

    def test_children_count(self):
        self.assertEqual(self._get('L1-A').children.count(), 2)   # L2-A1, L2-A2
        self.assertEqual(self._get('L2-A1').children.count(), 2)  # L3-A1a, L3-A1b
        self.assertEqual(self._get('L3-A1a').children.count(), 2) # L4-A1a-i, L4-A1a-ii
        self.assertEqual(self._get('L5-B2a-i-alpha').children.count(), 0)


class TestSeedGenresStructure(BaseTestCase):
    """Проверяем что _build_db_tree восстанавливает исходное дерево."""

    def setUp(self):
        super().setUp()
        _seed_genres(TEST_TREE, parent=None)

    def test_tree_roundtrip(self):
        restored = _build_db_tree(parent_id=None)
        # Сравниваем как множества имён, игнорируя порядок вставки
        self.assertEqual(
            _names_set(restored),
            _names_set(TEST_TREE),
        )


def _names_set(tree) -> set:
    """Все имена в дереве рекурсивно."""
    result = set()
    for name, children in tree:
        result.add(name)
        result |= _names_set(children)
    return result


class TestSeedGenresIdempotent(BaseTestCase):

    def test_double_seed_no_duplicates(self):
        _seed_genres(TEST_TREE, parent=None)
        _seed_genres(TEST_TREE, parent=None)
        self.assertEqual(Genre.select().count(), len(_ALL_NAMES))


class TestSeedEditions(BaseTestCase):

    def setUp(self):
        super().setUp()
        seed_reference_data()

    def test_editions_count(self):
        self.assertEqual(Edition.select().count(), 10)

    def test_editions_names(self):
        names = {e.name for e in Edition.select()}
        expected = {
            'Первое', 'Второе', 'Третье', 'Четвёртое', 'Пятое',
            'Шестое', 'Седьмое', 'Восьмое', 'Девятое', 'Десятое',
        }
        self.assertEqual(names, expected)

    def test_seed_idempotent(self):
        seed_reference_data()
        self.assertEqual(Edition.select().count(), 10)


if __name__ == '__main__':
    unittest.main()
