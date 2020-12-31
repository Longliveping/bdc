import unittest
from flask import current_app
from app import create_app, db
from app.models import Word, Wheres, Sentence, Mydict, sentences_words_relations
import os


def drop_everything():
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

    con = db.engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(db.engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(db.ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()

def get_file(filetype):
    sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        file = os.path.join(sourcedir, basename)
        basename = os.path.basename(file)
        extention = basename.split('.')[1]
        if extention == filetype:
            return file

class WordsTestCase(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        # Word.importfile(get_file())
        # Mydict.imports()


    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        # drop_everything()
        cls.app_context.pop()

    def test_sentences_to_words(self):
        Sentence.import_sentence_to_words(get_file())
        count = sentences_words_relations.query.count()
        self.assertTrue(count>0)

    def test_import_mydict(self):
        Mydict.imports()
        count = Mydict.query.count()
        self.assertTrue(count>0)

    def test_import_sentence(self):
        Sentence.import_sentence(get_file('txt'))
        count = Sentence.query.count()
        self.assertTrue(count>0)

    def test_create_words_to_wheres(self):
        pass

    def test_import_wheres(self):
        Wheres.import_wheres(get_file('txt'))
        count = Wheres.query.count()
        self.assertTrue(count>0)

    def test_import_word(self):
        Word.import_words(get_file('csv'))
        count = Word.query.count()
        self.assertTrue(count>0)



