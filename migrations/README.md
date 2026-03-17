# Миграции базы данных

Миграции применяются автоматически при открытии БД. Уже применённые скрипты
повторно не запускаются. Файлы миграций **никогда не удаляются** — они нужны
для разворачивания БД на новых устройствах.

## Именование файлов

```
NNN_короткое_описание.py
```

Примеры: `002_add_language_to_book.py`, `003_rename_tag_column.py`

Номера должны быть уникальными и идти по порядку — runner применяет миграции
в лексикографическом порядке по имени файла.

## Шаблон скрипта

```python
# migrations/NNN_описание.py
from playhouse.migrate import migrate as run_migrate
from peewee import CharField  # нужные типы полей


def migrate(migrator):
    run_migrate(
        migrator.add_column('table_name', 'column_name', CharField(default='')),
    )
```

> Важно: внутри файла функция называется `migrate`, поэтому хелпер из
> `playhouse.migrate` импортируется как `run_migrate` во избежание конфликта.

## Доступные операции migrator

| Операция | Пример |
|---|---|
| Добавить колонку | `migrator.add_column('books', 'language', CharField(default='ru'))` |
| Удалить колонку | `migrator.drop_column('books', 'old_field')` |
| Переименовать колонку | `migrator.rename_column('books', 'old', 'new')` |
| Переименовать таблицу | `migrator.rename_table('old_name', 'new_name')` |
| Добавить индекс | `migrator.add_index('books', ('title',), unique=False)` |
| Удалить индекс | `migrator.drop_index('books', 'index_name')` |

Полный список: [документация playhouse.migrate](https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations)

## Добавление нового поля

Нужно сделать два изменения — в модели и в миграции.

**1. Обновить модель** (`src/database/models/book.py`):

```python
class Book(BaseModel):
    ...
    language = CharField(default='ru', null=True)  # ← добавить
```

**2. Написать миграцию** (`migrations/002_add_language_to_book.py`):

```python
from playhouse.migrate import migrate as run_migrate
from peewee import CharField


def migrate(migrator):
    run_migrate(
        migrator.add_column('books', 'language', CharField(default='ru', null=True)),
    )
```

## Изменение типа поля

SQLite не поддерживает `ALTER COLUMN`, поэтому изменить тип напрямую нельзя.
Нужно: переименовать старую колонку → добавить новую → скопировать данные → удалить старую.

**1. Обновить тип в модели** (`src/database/models/book.py`):

```python
# было: pages = IntegerField(null=True)
pages = CharField(max_length=20, null=True)  # ← новый тип
```

**2. Написать миграцию** (`migrations/003_change_pages_type.py`):

```python
from playhouse.migrate import migrate as run_migrate
from peewee import CharField


def migrate(migrator):
    # Шаг 1: переименовать старую колонку
    run_migrate(migrator.rename_column('books', 'pages', 'pages_old'))

    # Шаг 2: добавить новую колонку с нужным типом
    run_migrate(migrator.add_column('books', 'pages', CharField(max_length=20, null=True)))

    # Шаг 3: скопировать данные (с преобразованием если нужно)
    migrator.database.execute_sql('UPDATE books SET pages = CAST(pages_old AS TEXT)')

    # Шаг 4: удалить старую колонку
    run_migrate(migrator.drop_column('books', 'pages_old'))
```
