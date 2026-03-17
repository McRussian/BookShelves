from peewee import AutoField, CharField

from src.database.database import BaseModel


class User(BaseModel):
    id = AutoField()
    login = CharField(max_length=50, unique=True, null=False)
    firstname = CharField(max_length=50, null=False)
    lastname = CharField(max_length=50, null=True)
    surname = CharField(max_length=50, null=True)

    class Meta:
        table_name = 'users'

    @property
    def full_name(self) -> str:
        parts = [self.lastname, self.firstname, self.surname]
        return ' '.join(p for p in parts if p)

    @property
    def display_name(self) -> str:
        """Полное имя с логином: 'Толстой Лев Николаевич (lev)'"""
        return f'{self.full_name} ({self.login})'
