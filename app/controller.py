import unittest
from flask import current_app
from app import create_app, db
from app.models import Word, Article, Sentence, SentenceWord, ArticleWord, SentenceReview, WordReview, MyWord, MySentence
import os
import re
import time
from utility.words import get_sentence, get_file_tokens,get_tokens, read_text, get_file_by_name, create_txt

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, value, tb):
        self.duration = time.time() - self.start

class DropTable():
    @classmethod
    def delete_table_records(self):
        db.session.remove()
        try:
            db.session.query(WordReview).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(SentenceReview).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(ArticleWord).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(SentenceWord).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(Sentence).delete()
            db.session.commit()
        except: pass
        # try:
        #     db.session.query(Review).delete()
        #     db.session.commit()
        # except: pass
        # try:
        #     db.session.query(Mydict).delete()
        #     db.session.commit()
        # except: pass
        try:
            db.session.query(MyWord).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(MySentence).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(Word).delete()
            db.session.commit()
        except: pass
        try:
            db.session.query(Article).delete()
            db.session.commit()
        except: pass

    @classmethod
    def drop_everything(self):
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

    @classmethod
    def drop_all(self):
        self.delete_table_records()
        self.drop_everything()
        db.drop_all()

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
        tokens = set(get_file_tokens(filename))
        exist = db.session.query(Word.word).all()
        exist =  set([e[0] for e in exist])
        not_exist = tokens - exist
        for n in not_exist:
            w = Word(word=n)
            db.session.add(w)
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
        article = db.session.query(Article).filter(Article.article == filename).first()

        sl = []
        sentences = get_sentence(get_file_by_name(filename))
        tokens_all = get_file_tokens(filename)
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

def import_myword():
    with Timer() as timer:
        sourcedir = current_app.config.get('MYWORD_FOLDER')
        file = os.path.join(sourcedir, 'myword.csv' )
        tokens = set(get_tokens(read_text((file))))
        exist = db.session.query(MyWord.word).all()
        exists = set([e[0] for e in exist])
        not_exists = tokens - exists
        for t in not_exists:
            m = MyWord(word=t)
            db.session.add(m)
        db.session.commit()
    print("took", timer.duration, "seconds")

def import_articleword(filename):
    import_word(filename)
    basename = os.path.basename(get_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(ArticleWord).join(Article).filter(Article.article == filename).first()
    if a:
        return

    with Timer() as timer:
        # insert ArticleWords
        db.session.remove()
        article = db.session.query(Article).filter(Article.article == filename).first()
        tokens = set(get_file_tokens(filename))
        words = db.session.query(Word).filter(Word.word.in_(tokens)).all()
        aw = [ArticleWord(article=article, word=w) for w in words]
        db.session.add_all(aw)
        db.session.commit()
    print("took", timer.duration, "seconds")

def show_artile_words(article_name):
    myword = db.session.query(MyWord.word).all()
    mywords = set([w[0] for w in myword])

    article_word = db.session.query(Word.word).join(ArticleWord).join(Article).filter(
        Article.article == article_name,
        Word.word.notin_(mywords)
    ).all()

    article_words = [w[0] for w in article_word]

    return article_words

def import_file(file):
    create_txt(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    import_article(filename)
    import_word(filename)
    import_sentence(filename)
    import_articleword(filename)