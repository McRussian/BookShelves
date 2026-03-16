from __future__ import annotations

from src.database.data import EDITIONS, GenreTree, GENRES, BOOK_TYPES

from src.database.models.book_type import BookType
from src.database.models.edition import Edition
from src.database.models.genre import Genre


def seed_reference_data() -> None:
    """Заполнить справочники начальными данными (идемпотентно)."""
    for name in EDITIONS:
        Edition.get_or_create(name=name)

    for name in BOOK_TYPES:
        BookType.get_or_create(name=name)

    _seed_genres(GENRES, parent=None)


def _seed_genres(tree: GenreTree, parent: Genre | None) -> None:
    for name, children in tree:
        genre, _ = Genre.get_or_create(name=name, defaults={'parent': parent})
        if children:
            _seed_genres(children, parent=genre)
