import importlib.util
from pathlib import Path

from peewee import CharField, Model
from playhouse.migrate import SqliteMigrator

DEFAULT_MIGRATIONS_DIR = Path(__file__).parent.parent.parent / 'migrations'


def run_migrations(database, migrations_dir: Path = DEFAULT_MIGRATIONS_DIR) -> list[str]:
    """Применяет все непримененные миграции к базе данных.

    Возвращает список имён применённых миграций.
    """
    class MigrationRecord(Model):
        name = CharField(primary_key=True)

        class Meta:
            table_name = 'migration'

    MigrationRecord._meta.database = database

    database.create_tables([MigrationRecord], safe=True)

    applied = {r.name for r in MigrationRecord.select()}
    migration_files = sorted(migrations_dir.glob('[0-9]*.py'))

    applied_now = []
    for path in migration_files:
        if path.stem in applied:
            continue

        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        migrator = SqliteMigrator(database)
        module.migrate(migrator)

        MigrationRecord.create(name=path.stem)
        applied_now.append(path.stem)

    return applied_now
