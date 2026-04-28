"""Удалить дублирующиеся записи в book_genres, book_tags, book_authors и добавить уникальные индексы."""


def migrate(migrator):
    db = migrator.database

    relations = [
        ('book_genres',  'book_id', 'genre_id'),
        ('book_tags',    'book_id', 'tag_id'),
        ('book_authors', 'book_id', 'author_id'),
    ]

    for table, col_a, col_b in relations:
        db.execute_sql(f"""
            DELETE FROM {table}
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM {table}
                GROUP BY {col_a}, {col_b}
            )
        """)

    for table, col_a, col_b in relations:
        index_name = f'{table}_{col_a}_{col_b}'
        db.execute_sql(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
            ON {table} ({col_a}, {col_b})
        """)
