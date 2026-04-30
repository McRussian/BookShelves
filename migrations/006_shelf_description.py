"""Добавление поля description в таблицу shelves."""
from peewee import TextField
from playhouse.migrate import migrate as run


def migrate(migrator):
    run(
        migrator.add_column('shelves', 'description', TextField(null=True)),
    )
