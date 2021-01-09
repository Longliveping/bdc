import unittest
from app import create_app, db
from app.models import Word, Article, Sentence, SentenceWord, ArticleWord, SentenceReview, WordReview, MyWord, MySentence
import os
from utility.words import get_sentence, get_file_tokens,get_tokens, read_text, get_file_by_name
from app.controller import import_word, import_myword, import_sentence, import_article, import_articleword, DropTable, show_artile_words

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

    # def test_import_article(self):
    #     import_article('103_')
    #     count = db.session.query(Article).count()
    #     self.assertTrue(count>0)
    #
    # def test_import_big_txt(self):
    #     import_word('103_')
    #     count = db.session.query(Word).count()
    #     self.assertTrue(count>0)
    #
    # def test_import_sentence(self):
    #     import_word('103_')
    #     import_sentence('103_')
    #     count = db.session.query(Sentence).count()
    #     self.assertTrue(count>0)
    #
    # def test_import_myword(self):
    #     import_myword()
    #     count = db.session.query(MyWord).count()
    #     self.assertTrue(count>0)
    #
    # def test_import_articleword(self):
    #     import_articleword('103_')
    #     count = db.session.query(ArticleWord).count()
    #     self.assertTrue(count>0)
    #
    # def test_show_artcle_word(self):
    #     basename = os.path.basename(get_file_by_name('103_'))
    #     filename = basename.split('.')[0]
    #     show_artile_words(filename)


    def test_query(self):
        remove_tokens = ('he','is')
        try:
            db.session.query(MyWord).filter(MyWord.word.in_(remove_tokens)).delete(synchronize_session='fetch')
            db.session.commit()
        except :
            print('error')



