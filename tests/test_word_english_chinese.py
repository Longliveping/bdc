import unittest
import os
from app import create_app
from flask import current_app
from utility.words import create_sentence_srt_json,_create_word_json,\
    read_file_by_name, read_word_json_file, _read_token_json,read_text, \
    read_sentence_json_file,_read_sentence_json, extract_text, read_file_by_type



class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()
    @unittest.skip('it takes time')
    def test_001_extract_text(self):
        file = os.path.join(current_app.config.get('TESTING_FOLDER'), 'Conversation.docx')
        extract_text(file)
    @unittest.skip('it takes time')
    def test_002_create_sentence_json(self):
        file = read_file_by_name('Conversation')
        basename = os.path.basename(file)
        dirname = os.path.dirname(file)
        json_file = os.path.join(dirname,basename.split('.')[0]+'_sentence.json')
        create_sentence_srt_json(file)
        self.assertTrue(os.path.exists(json_file))

    @unittest.skip('it takes time')
    def test_003_create_word_json(self):
        file = read_file_by_name('Conversation')
        basename = os.path.basename(file)
        dirname = os.path.dirname(file)
        json_file = os.path.join(dirname,basename.split('.')[0]+'_word.json')
        _create_word_json(file)
        self.assertTrue(os.path.exists(json_file))
    @unittest.skip('it takes time')
    def test_004_get_word_json(self):
        json_file = read_word_json_file('Conversation')
        words = _read_token_json(json_file)
        self.assertTrue(len(words) == 1102)
    @unittest.skip('it takes time')
    def test_005_get_sentence_json(self):
        json_file = read_sentence_json_file('Conversation')
        sentences = _read_sentence_json(json_file)
        self.assertTrue(len(sentences) == 1425)