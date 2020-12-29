from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db #, login_manager
import csv
import os
<<<<<<< HEAD
import re
from utility.words import get_sentence, create_txt, create_token, update_target
from pprint import pprint

def db_update_record(r):
    db.session.add(r)
    try:
        db.session.commit()
    except:
        db.session.rollback()
=======
from utility.words import get_text, create_token, get_sentence
>>>>>>> update with sentence

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    chinese = db.Column(db.String(64))
    noshow = db.Column(db.Boolean, default=False)
    known = db.Column(db.Boolean, default=False)
    unknown = db.Column(db.Boolean, default=True)
    blurry = db.Column(db.Boolean, default=False)
    review_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    noshow_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    wheres =db.relationship('Wheres', backref='word', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)

    @staticmethod
    def import_words(file):
        data = list(csv.reader(open(file)))
        for d in data:
            w = Word.query.filter_by(word=d[0]).first()
            if not w:
                w = Word(word=d[0])
            db.session.add(w)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    @staticmethod
    def imports():
        update_target()
        target_path = os.path.join(os.getcwd(), 'utility/source/friends/season_01/target')
        for basename in os.listdir(target_path):
            file = os.path.join(target_path, basename)
            extname = basename.split('.')[1]
            if extname == 'csv':
                Word.import_words(file)
                Wheres.import_wheres(file)
            elif extname == 'txt':
                Sentence.import_sentence(file)
        Word.update_noshow()

    @staticmethod
    def importfile(file):
        txtfile = create_txt(file)
        csvfile = create_token(txtfile)
        Word.import_words(csvfile)
        Wheres.import_wheres(csvfile)
        Sentence.import_sentence(txtfile)

    @staticmethod
    def update_noshow(count=-1):
        if count == -1:
            mydict = Mydict.query.all()
        else:
            mydict = Mydict.query.order_by(Mydict.timestamp.desc()).limit(count).all()
        for d in mydict:
            print("update no show", count, d)
            w = Word.query.filter_by(word=d.word).first()
            if w:
                w.noshow = True
            else:
                w = Word(word=d.word,
                         noshow=True,
                         noshow_timestamp=datetime.utcnow()
                         )
            db_update_record(w)

    @staticmethod
    def importfile(file):
        basedir = os.path.dirname(file)
        filename = os.path.basename(file)
        txtfilename = filename.split(".")[0]+'.txt'
        csvfilename = filename.split(".")[0]+'.csv'
        csvfile = os.path.join(basedir, csvfilename)
        wfile = os.path.join(basedir, txtfilename)
        with open(wfile, 'a') as f:
            lines = get_text(file)
            f.write(lines)
        create_token(wfile)

        print(csvfile)
        if os.path.exists(csvfile):
            reader = csv.reader(open(csvfile))
            data = list(reader)
            for d in data:
                w = Word.query.filter_by(word=d[0]).first()
                if not w:
                    w = Word(word=d[0])
                db.session.add(w)
            try:
                db.session.commit()
            except:
                db.session.rollback()

            for d in data:
                w = Word.query.filter_by(word=d[0]).first()
                wh = Wheres(word_id=w.id,wheres=filename[:20],frequency=d[1])
                db.session.add(wh)
            try:
                db.session.commit()
            except:
                db.session.rollback()

    @staticmethod
    def updatebymydict():
        mydict = Mydict.query.all()
        for d in mydict:
            w = Word.query.filter_by(word=d.word).first()
            if w:
                w.noshow=True
                w.noshow_timestamp=datetime.utcnow()
            else:
                w = Word(word=d.word,
                         noshow=True,
                         noshow_timestamp=datetime.utcnow()
                         )
            db.session.add(w)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def to_json(self):
        json_word = {
            'url': url_for('api.get_word', id=self.id),
            'word': self.word
        }

    @staticmethod
    def from_json(json_word):
        word = json_word.get('word')
        if word is None or word == '':
            raise ValidationError('post does not have a body')
        return Word(word=word)

    def __repr__(self):
        return '<Word %r>' % self.word

class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text())
    wheres = db.Column(db.String(256))

    @staticmethod
<<<<<<< HEAD
    def import_sentence(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        sentences = get_sentence(file)
        for s in sentences:
            exist = Sentence.query.filter_by(wheres=filename).filter_by(sentence=s).first()
            if not exist:
                sen = Sentence(sentence=s,  wheres=filename)
=======
    def importfile(file):
        basedir = os.path.dirname(file)
        filename = os.path.basename(file)
        txtfilename = filename.split(".")[0]+'.txt'
        # csvfilename = filename.split(".")[0]+'.csv'
        # csvfile = os.path.join(basedir, csvfilename)
        wfile = os.path.join(basedir, txtfilename)
        with open(wfile, 'a') as f:
            lines = get_text(file)
            f.write(lines)
        # create_token(wfile)
        #
        # if os.path.exists(csvfile):
        #     reader = csv.reader(open(csvfile))
        #     data = list(reader)
        #     for d in data:
        #         w = Word.query.filter_by(word=d[0]).first()
        #         if not w:
        #             w = Word(word=d[0])
        #             db.session.add(w)
        #     try:
        #         db.session.commit()
        #     except:
        #         db.session.rollback()

        sentences = get_sentence(wfile)
        for s in sentences:
            exist = Sentence.query.filter_by(wheres=filename[:20]).filter_by(sentence=s).first()
            if not exist:
                sen = Sentence(sentence=s,  wheres=filename[:20])
>>>>>>> update with sentence
                db.session.add(sen)
        try:
            db.session.commit()
        except:
            db.session.rollback()

<<<<<<< HEAD
    @staticmethod
    def importfile(file):
        txtfile = create_txt(file)
        Sentence.import_sentence(txtfile)

=======
>>>>>>> update with sentence
    def __init__(self, **kwargs):
        super(Sentence, self).__init__(**kwargs)

    def __repr__(self):
        return '<Sentence %r>' % self.sentence

class Wheres(db.Model):
    __tablename__ = 'wheres'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    frequency = db.Column(db.Integer)
    wheres = db.Column(db.String(256))

    @staticmethod
    def import_wheres(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        data = list(csv.reader(open(file)))
        for d in data:
            w = Word.query.filter_by(word=d[0]).first()
            exist = Wheres.query.filter_by(wheres=filename).filter_by(word_id=w.id).first()
            if not exist:
                wh = Wheres(word_id=w.id,wheres=filename,frequency=d[1])
                db.session.add(wh)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def __init__(self, **kwargs):
        super(Wheres, self).__init__(**kwargs)

    def __repr__(self):
        return '<Wheres %r>' % self.wheres

class Mydict(db.Model):
    __tablename__ = 'mydicts'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


    @staticmethod
    def imports():
        basedir = os.path.join(os.getcwd(), 'utility/mydict')
        for filename in os.listdir(basedir):
            f = open(os.path.join(basedir, filename))
            reader = csv.reader(f)
            data = list(reader)
            for d in data:
                w = Mydict(word=d[0])
<<<<<<< HEAD
                db_update_record(w)

        Word.update_noshow()
=======
                db.session.add(w)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
>>>>>>> update with sentence


    def __init__(self, **kwargs):
        super(Mydict, self).__init__(**kwargs)

    def __repr__(self):
        return '<Mydict %r>' % self.word