"""Добавить уникальный индекс на publishers.name."""
from playhouse.migrate import migrate as run_migrate


def migrate(migrator):
    run_migrate(
        migrator.add_index('publishers', ('name',), unique=True),
    )
