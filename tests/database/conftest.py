import unittest
from peewee import SqliteDatabase

from src.database.models import ALL_MODELS


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db = SqliteDatabase(':memory:', pragmas={'foreign_keys': 1})
        self.db.bind(ALL_MODELS, bind_refs=False, bind_backrefs=False)
        self.db.connect()
        self.db.create_tables(ALL_MODELS)

    def tearDown(self):
        self.db.drop_tables(ALL_MODELS)
        self.db.close()
