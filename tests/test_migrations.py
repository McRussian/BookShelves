import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from peewee import CharField, IntegerField, Model, SqliteDatabase
from playhouse.migrate import SqliteMigrator, migrate as peewee_migrate

from src.database.migrations import run_migrations


def make_db() -> SqliteDatabase:
    return SqliteDatabase(':memory:', pragmas={'foreign_keys': 1})


def write_migration(directory: Path, name: str, body: str) -> None:
    (directory / name).write_text(textwrap.dedent(body))


class TestRunMigrations(unittest.TestCase):

    def setUp(self):
        self.db = make_db()
        self.db.connect()
        self.tmp = TemporaryDirectory()
        self.migrations_dir = Path(self.tmp.name)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    # ── вспомогательные методы ────────────────────────────────────────────────

    def _migration_table_exists(self) -> bool:
        return 'migration' in self.db.get_tables()

    def _applied(self) -> set[str]:
        return {row[0] for row in self.db.execute_sql('SELECT name FROM migration')}

    def _columns(self, table: str) -> set[str]:
        return {row[1] for row in self.db.execute_sql(f'PRAGMA table_info({table})')}

    # ── тесты ─────────────────────────────────────────────────────────────────

    def test_creates_migration_table(self):
        run_migrations(self.db, self.migrations_dir)
        self.assertIn('migration', self.db.get_tables())

    def test_empty_dir_runs_without_errors(self):
        applied = run_migrations(self.db, self.migrations_dir)
        self.assertEqual(applied, [])

    def test_single_migration_applied(self):
        # Создаём тестовую таблицу
        self.db.execute_sql('CREATE TABLE items (id INTEGER PRIMARY KEY)')

        write_migration(self.migrations_dir, '001_add_name.py', """
            from playhouse.migrate import migrate as run_migrate
            from peewee import CharField

            def migrate(migrator):
                run_migrate(migrator.add_column('items', 'name', CharField(default='')))
        """)

        applied = run_migrations(self.db, self.migrations_dir)

        self.assertEqual(applied, ['001_add_name'])
        self.assertIn('name', self._columns('items'))

    def test_migration_recorded_in_table(self):
        self.db.execute_sql('CREATE TABLE items (id INTEGER PRIMARY KEY)')

        write_migration(self.migrations_dir, '001_add_name.py', """
            from playhouse.migrate import migrate as run_migrate
            from peewee import CharField

            def migrate(migrator):
                run_migrate(migrator.add_column('items', 'name', CharField(default='')))
        """)

        run_migrations(self.db, self.migrations_dir)
        self.assertIn('001_add_name', self._applied())

    def test_migration_not_applied_twice(self):
        self.db.execute_sql('CREATE TABLE items (id INTEGER PRIMARY KEY)')

        write_migration(self.migrations_dir, '001_add_name.py', """
            from playhouse.migrate import migrate as run_migrate
            from peewee import CharField

            def migrate(migrator):
                run_migrate(migrator.add_column('items', 'name', CharField(default='')))
        """)

        run_migrations(self.db, self.migrations_dir)
        # Второй запуск — ничего нового
        applied = run_migrations(self.db, self.migrations_dir)
        self.assertEqual(applied, [])

    def test_migrations_applied_in_order(self):
        self.db.execute_sql('CREATE TABLE items (id INTEGER PRIMARY KEY)')
        order = []

        write_migration(self.migrations_dir, '001_first.py', """
            def migrate(migrator):
                pass
        """)
        write_migration(self.migrations_dir, '002_second.py', """
            def migrate(migrator):
                pass
        """)
        write_migration(self.migrations_dir, '003_third.py', """
            def migrate(migrator):
                pass
        """)

        applied = run_migrations(self.db, self.migrations_dir)
        self.assertEqual(applied, ['001_first', '002_second', '003_third'])

    def test_only_new_migrations_applied_on_second_run(self):
        self.db.execute_sql('CREATE TABLE items (id INTEGER PRIMARY KEY, val INTEGER DEFAULT 0)')

        write_migration(self.migrations_dir, '001_first.py', """
            def migrate(migrator):
                pass
        """)
        run_migrations(self.db, self.migrations_dir)

        write_migration(self.migrations_dir, '002_add_name.py', """
            from playhouse.migrate import migrate as run_migrate
            from peewee import CharField

            def migrate(migrator):
                run_migrate(migrator.add_column('items', 'name', CharField(default='')))
        """)

        applied = run_migrations(self.db, self.migrations_dir)
        self.assertEqual(applied, ['002_add_name'])
        self.assertIn('name', self._columns('items'))

    def test_non_migration_files_ignored(self):
        (self.migrations_dir / 'README.md').write_text('docs')
        (self.migrations_dir / 'helper.py').write_text('x = 1')

        applied = run_migrations(self.db, self.migrations_dir)
        self.assertEqual(applied, [])


if __name__ == '__main__':
    unittest.main()
