from peewee import AutoField, BooleanField, CharField, ForeignKeyField, fn, IntegerField, TextField

from src.database.database import BaseModel
from src.database.models.book import Book
from src.database.models.user import User


class Shelf(BaseModel):
    id = AutoField()
    name = CharField(max_length=100)
    description = TextField(null=True)
    user = ForeignKeyField(User, backref='shelves', on_delete='CASCADE')
    is_active = BooleanField(default=True)

    class Meta:
        table_name = 'shelves'
        indexes = ((('user_id', 'name'), True),)

    @classmethod
    def for_user(cls, user) -> list['Shelf']:
        return list(cls.select().where(cls.user == user).order_by(fn.LOWER(cls.name)))

    def add_book(self, book: Book) -> 'ShelfBook':
        max_pos = (
            ShelfBook.select(fn.MAX(ShelfBook.position))
            .where(ShelfBook.shelf == self)
            .scalar()
        ) or 0
        obj, _ = ShelfBook.get_or_create(
            shelf=self, book=book,
            defaults={'position': max_pos + 1},
        )
        return obj

    def get_books(self) -> list[Book]:
        ids = [
            row[0] for row in
            ShelfBook.select(ShelfBook.book)
            .where(ShelfBook.shelf == self)
            .order_by(ShelfBook.position)
            .tuples()
        ]
        if not ids:
            return []
        books_by_id = {b.id: b for b in Book.select().where(Book.id.in_(ids))}
        return [books_by_id[i] for i in ids if i in books_by_id]

    def remove_book(self, book: Book) -> None:
        ShelfBook.delete().where(
            ShelfBook.shelf == self,
            ShelfBook.book == book,
        ).execute()


class ShelfBook(BaseModel):
    shelf = ForeignKeyField(Shelf, backref='shelf_books', on_delete='CASCADE')
    book = ForeignKeyField(Book, backref='shelf_books', on_delete='CASCADE')
    position = IntegerField(default=0)

    class Meta:
        table_name = 'shelf_books'
        indexes = ((('shelf_id', 'book_id'), True),)
