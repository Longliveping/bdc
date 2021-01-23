import unittest
from app import create_app, db
from flask import current_app
from app.models import Word, Article, Sentence, SentenceWord, ArticleWord, SentenceReview, WordReview, MyWord, MySentence
import os
from utility.words import get_token, \
    read_text, read_file_by_name, read_word_by_file, get_valid_token, _create_sentence
from app.controller import Timer,import_word, import_myword, import_sentence, \
    import_article, import_articleword, show_artile_words,db_init_word, import_url

class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    @unittest.skip('it takes time')
    def test_re(self):
        file = os.path.join(current_app.config.get('UPLOAD_FOLDER'), '2020s-most-popular-topics32.txt')
        _create_sentence(file)

    @unittest.skip('it takes time')
    def test_import_url(self):
        url = 'https://blog.khanacademy.org/2020s-most-popular-topics-courses-conversations-on-khan-academy/'
        import_url(url)
        pass







