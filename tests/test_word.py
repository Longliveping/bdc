import unittest
import os
from app import create_app
from flask import current_app
from utility.words import article_file, my_word, articles

class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.article = article_file

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    @unittest.skip('it takes time')
    def test_001_extract_text(self):
        file = os.path.join(current_app.config.get('TESTING_FOLDER'), 'Conversation.docx')
        self.article.load(file)
        self.article.update_text(self.article.get_text())
        self.assertTrue(self.article.get_token())
        print(len(self.article.get_token()))
        print(len(self.article.get_word()))
        print(len(self.article.get_sentence()))

    def test_002_articles(self):
        articles.get_articles()
        print(articles.get_articlename())
        print(articles.get_noshow())
        print(articles.get_wordcount())