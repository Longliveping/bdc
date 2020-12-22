from datetime import datetime
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
    sentences = db.relationship('Sentence', backref='word', lazy='dynamic')
    wheres =db.relationship('Wheres', backref='word', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)

    @staticmethod
    def imports():
        basedir = os.path.join(os.getcwd(), 'utility/source/friends/season_01/target')
        for file in os.listdir(basedir):
            if file[-3:] == 'csv':
                filename = os.path.join(basedir,file)
                reader = csv.reader(open(filename))
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
                    wh = Wheres(word_id=w.id,wheres=file[:3],frequency=d[1])
                    db.session.add(wh)
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
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    sentence = db.Column(db.Text())
    wheres = db.Column(db.String(256))

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
        basedir = os.path.join(os.getcwd(), 'utility')
        file = open(os.path.join(basedir, 'mydict.csv'))
        reader = csv.reader(file)
        data = list(reader)
        for d in data:
            w = Mydict(word=d[0])
            db.session.add(w)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def __init__(self, **kwargs):
        super(Mydict, self).__init__(**kwargs)

    def __repr__(self):
        return '<Mydict %r>' % self.word