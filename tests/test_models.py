import unittest
from flask import current_app
from app import create_app, db
from app.models import Word, Article, Sentence, Mydict, Review, SentenceWord
import os
import re
import time
from utility.words import get_sentence, get_tokens, read_text, get_file_by_name


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, value, tb):
        self.duration = time.time() - self.start

def delete_table_records():
    db.session.query(SentenceWord).delete()
    db.session.query(Sentence).delete()
    db.session.query(Mydict).delete()
    db.session.query(Word).delete()
    db.session.query(Article).delete()
    db.session.commit()

def drop_everything():
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

    con = db.engine.connect()
    print(con)
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

def import_article(filename):
    basename = os.path.basename(get_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(Article).filter(Article.article == filename).first()
    if not a:
        a1 = Article(article=filename)
        db.session.add(a1)
        db.session.commit()

def import_word(filename):
    with Timer() as timer:
        tokens = set(get_tokens(read_text(get_file_by_name(filename))))
        exist = db.session.query(Word.word).all()
        exist =  set([e[0] for e in exist])
        not_exist = tokens - exist
        for n in not_exist:
            w = Word(word=n)
            db.session.add(w)
        db.session.new
        db.session.commit()
    print("took", timer.duration, "seconds")

def import_sentence(filename):
    basename = os.path.basename(get_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(Sentence).join(Article).filter(Article.article == filename).first()
    if a:
        return

    with Timer() as timer:
        # insert SentenceWords
        db.session.remove()
        article = db.session.query(Article).first()

        sl = []
        sentences = get_sentence(get_file_by_name(filename))
        tokens_all = get_tokens(read_text(get_file_by_name(filename)))
        words_all = db.session.query(Word).filter(Word.word.in_(tokens_all)).all()
        for sentence in sentences:
            tokens = get_tokens(sentence)
            s = Sentence(sentence=sentence, article=article)
            w = [w for w in words_all if w.word in tokens]
            sw = [SentenceWord(word=i) for i in w]
            s.sentencewords = sw
            sl.append(s)
        db.session.add_all(sl)
        db.session.commit()

    print("took", timer.duration, "seconds")

def import_dict():
    with Timer() as timer:
        sourcedir = current_app.config.get('MYDICT_FOLDER')
        file = os.path.join(sourcedir, 'mydict.csv' )

        tokens = set(get_tokens(read_text((file))))
        exist = db.session.query(Word.word).join(Mydict).all()
        exist =  set([e[0] for e in exist])
        not_exist = tokens - exist
        for t in not_exist:
            m = db.session.query(Word).join(Mydict).filter(Word.word==t).first()
            if not m:
                w = db.session.query(Word).filter(Word.word == t).first()
                if not w:
                    w = Word(word=t)
                    m = Mydict(word=w)
                    db.session.add(w)
                    db.session.add(m)
                else:
                    m = Mydict(word=w)
                    db.session.add(m)
        db.session.new
        db.session.commit()
    print("took", timer.duration, "seconds")


class WordsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        # delete_table_records()
        # db.drop_all()
        # drop_everything()
        db.session.remove()
        cls.app_context.pop()

    def test_import_article(self):
        import_article('103_')
        count = db.session.query(Article).count()
        self.assertTrue(count>0)

    def test_import_big_txt(self):
        import_word('big')
        count = db.session.query(Word).count()
        self.assertTrue(count>0)

    def test_import_mydict(self):
        import_dict()
        count = db.session.query(Mydict).count()
        self.assertTrue(count>0)

    def test_import_sentence(self):
        import_word('103_')
        import_sentence('103_')
        count = db.session.query(Sentence).count()
        self.assertTrue(count>0)






