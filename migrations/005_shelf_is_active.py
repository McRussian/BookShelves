"""Добавление поля is_active в таблицу shelves."""
from peewee import BooleanField
from playhouse.migrate import migrate as run


def migrate(migrator):
    run(
        migrator.add_column('shelves', 'is_active', BooleanField(default=True)),
    )
