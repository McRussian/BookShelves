from peewee import AutoField, CharField, ForeignKeyField, JOIN, ModelSelect

from src.database.database import BaseModel


class Author(BaseModel):
    id = AutoField()
    firstname = CharField(max_length=50, null=False)
    lastname = CharField(max_length=50, null=True)
    surname = CharField(max_length=50, null=True)   # отчество
    comment = CharField(max_length=200, null=True)

    class Meta:
        db_table = 'authors'

    @property
    def full_name(self) -> str:
        parts = [self.lastname, self.firstname, self.surname]
        return ' '.join(p for p in parts if p)

    @property
    def aliases_str(self) -> str:
        """Псевдонимы через запятую: 'Ричард Бахман, Джон Свиффен'"""
        return ', '.join(a.alias for a in self.aliases)

    @property
    def display_name(self) -> str:
        """ФИО с псевдонимами в скобках: 'Стивен Кинг (Ричард Бахман)'"""
        name = self.full_name
        aliases = self.aliases_str
        return f'{name} ({aliases})' if aliases else name

    @property
    def display_name_by_alias(self) -> str:
        """Первый псевдоним с ФИО в скобках: 'Ричард Бахман (Стивен Кинг)'"""
        aliases = list(self.aliases)
        if not aliases:
            return self.full_name
        return f'{aliases[0].alias} ({self.full_name})'

    def delete_instance(self, *args, **kwargs):
        """Удаляет автора вместе со всеми его псевдонимами."""
        AuthorAlias.delete().where(AuthorAlias.author == self).execute()
        return super().delete_instance(*args, **kwargs)

    @classmethod
    def search(cls, query: str) -> ModelSelect:
        """Поиск по ФИО и псевдонимам. Возвращает запрос, можно дополнять."""
        return (
            cls
            .select()
            .join(AuthorAlias, JOIN.LEFT_OUTER)
            .where(
                cls.firstname.contains(query) |
                cls.lastname.contains(query) |
                cls.surname.contains(query) |
                AuthorAlias.alias.contains(query)
            )
            .distinct()
        )


class AuthorAlias(BaseModel):
    id = AutoField()
    author = ForeignKeyField(Author, backref='aliases', on_delete='CASCADE')
    alias = CharField(max_length=100, null=False)

    class Meta:
        db_table = 'author_aliases'
