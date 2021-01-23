import unittest
import os
from app import create_app
from flask import current_app
from utility.words import create_sentence_english_json,_create_word_json,\
    read_file_by_name, read_word_json_file, _read_token_json,read_text, \
    read_sentence_json_file,_read_sentence_json, extract_text, \
    read_file_by_type, create_sentence_english_json, ArticleFile

class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.article = ArticleFile()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    # @unittest.skip('it takes time')
    def test_001_extract_text(self):
        file = os.path.join(current_app.config.get('TESTING_FOLDER'), 'Conversation.docx')
        self.article.load(file)
        self.article.update_text(self.article.get_text())
        self.assertTrue(self.article.get_token())
        print(len(self.article.get_token()))
        print(len(self.article.get_word()))
        print(len(self.article.get_sentence()))