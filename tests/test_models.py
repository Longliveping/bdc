import unittest
from flask import current_app
from app import create_app, db
from app.models import Word, Wheres, Sentence, Mydict

class WordsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        Word.imports()
        Mydict.imports()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_import_word(self):
        count = Word.query.count()
        self.assertTrue(count>0)

    def test_import_sentence(self):
        count = Sentence.query.count()
        self.assertTrue(count>0)

    def test_import_wheres(self):
        count = Wheres.query.count()
        self.assertTrue(count>0)

    def test_import_mydict(self):
        count = Mydict.query.count()
        self.assertTrue(count>0)