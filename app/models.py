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
import re
from utility.words import get_sentence, create_txt, create_token, update_target
from pprint import pprint

def db_update_record(r):
    db.session.add(r)
    try:
        db.session.commit()
    except:
        db.session.rollback()

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
        if current_app.config.get('TESTING'):
            sourcedir = current_app.config.get('TESTING_FOLDER')
            target_path = os.path.join(sourcedir, 'target')
        else:
            sourcedir = current_app.config.get('SOURCE_FOLDER')
            target_path = os.path.join(sourcedir, 'friends/season_01/target')

        update_target(sourcedir)

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
    def import_sentence(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        sentences = get_sentence(file)
        for s in sentences:
            exist = Sentence.query.filter_by(wheres=filename).filter_by(sentence=s).first()
            if not exist:
                sen = Sentence(sentence=s,  wheres=filename)
                db.session.add(sen)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    @staticmethod
    def importfile(file):
        txtfile = create_txt(file)
        Sentence.import_sentence(txtfile)

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
    __tablename__ = 'mydict'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


    @staticmethod
    def imports():
        basedir = current_app.config.get('MYDICT_FOLDER')
        if current_app.config.get('TESTING'):
            basedir = os.path.join(basedir, 'testing')

        for filename in os.listdir(basedir):
            f = open(os.path.join(basedir, filename))
            reader = csv.reader(f)
            data = list(reader)
            for d in data:
                w = Mydict(word=d[0])
                db_update_record(w)


        Word.update_noshow()



    def __init__(self, **kwargs):
        super(Mydict, self).__init__(**kwargs)

    def __repr__(self):
        return '<Mydict %r>' % self.word