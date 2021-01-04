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

sentences_words_relations = db.Table('sentences_words',
                                     db.Column('sentence_id', db.Integer, db.ForeignKey('sentences.id')),
                                     db.Column('word_id', db.Integer, db.ForeignKey('words.id'))
                                     )

words_articles_relations = db.Table('words_articles',
                                    db.Column('word_id', db.Integer, db.ForeignKey('words.id')),
                                    db.Column('articles_id', db.Integer, db.ForeignKey('articles.id'))
                                    )

sentences_articles_relations = db.Table('sentences_articles',
                                        db.Column('sentence_id', db.Integer, db.ForeignKey('sentences.id')),
                                        db.Column('articles_id', db.Integer, db.ForeignKey('articles.id'))
                                        )

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', secondary=words_articles_relations)

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
                Article.import_articles(file)
            elif extname == 'txt':
                Sentence.import_sentence(file)

        Word.update_noshow()

    @staticmethod
    def importfile(file):
        txtfile = create_txt(file)
        csvfile = create_token(txtfile)
        Word.import_words(csvfile)
        Article.import_articles(csvfile)
        Sentence.import_sentence(txtfile)


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

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    chinese = db.Column(db.String(64))
    noshow = db.Column(db.Boolean, default=False)
    known = db.Column(db.Boolean, default=False)
    unknown = db.Column(db.Boolean, default=True)
    blurry = db.Column(db.Boolean, default=False)
    review_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    noshow_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    word = db.relationship('Word')

    @staticmethod
    def update_noshow(count=-1):
        if count == -1:
            mydict = Mydict.query.all()
        else:
            mydict = Mydict.query.order_by(Mydict.timestamp.desc()).limit(count).all()
        for d in mydict:
            print("update no show", count, d)
            # w = Review.query.filter_by(word=d.word).first()
            # if w:
            #     w.noshow = True
            # else:
            #     w = Word(word=d.word,
            #              noshow=True,
            #              noshow_timestamp=datetime.utcnow()
            #              )
            # db_update_record(w)

    def __init__(self, **kwargs):
        super(Review, self).__init__(**kwargs)

    def __repr__(self):
        return '<Review %r>' % self.id

class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text())
    words = db.relationship('Sentence', secondary=sentences_words_relations)
    articles = db.relationship('Article', secondary=sentences_articles_relations)


    @staticmethod
    def import_sentence(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        sentences = get_sentence(file)
        for s in sentences:
            exist = Sentence.query.filter_by(sentence=s).first()
            if not exist:
                sen = Sentence(sentence=s)
                db.session.add(sen)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def import_sentence_to_words(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        sentences = get_sentence(file)
        for s in sentences:
            sen = Sentence.query.filter_by(sentence=s).first()
            if sen:
                sen.words = []
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

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    # word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    # frequency = db.Column(db.Integer)
    article = db.Column(db.String(256))

    @staticmethod
    def import_articles(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        w = Article(article=filename)
        db_update_record(w)

    def add_articles_to_words(file):
        basename = os.path.basename(file)
        filename = basename.split('.')[0]
        data = list(csv.reader(open(file)))
        for d in data:
            w = Word.query.filter_by(word=d[0]).first()
            exist = Article.query.filter_by(article=filename).filter_by(word_id=w.id).first()
            if not exist:
                wh = Article(word_id=w.id, article=filename, frequency=d[1])
                db.session.add(wh)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)

    def __repr__(self):
        return '<Article %r>' % self.article

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


        Review.update_noshow()



    def __init__(self, **kwargs):
        super(Mydict, self).__init__(**kwargs)

    def __repr__(self):
        return '<Mydict %r>' % self.word


class Sequence(db.Model):
    __tablename__ = 'sequences'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __init__(self, **kwargs):
        super(Sequence, self).__init__(**kwargs)

    def __repr__(self):
        return '<Sequence %r>' % self.name

class Annotation(db.Model):
    __tablename__ = 'annotations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'))
    sequence = db.relationship('Sequence')

    def __init__(self, **kwargs):
        super(Annotation, self).__init__(**kwargs)

    def __repr__(self):
        return '<Annotation %r>' % self.name

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    town = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    updated_on = db.Column(db.DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, **kwargs):
        super(Customer, self).__init__(**kwargs)

    def __repr__(self):
        return '<Customer %r>' % self.id

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(200), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2),  nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    db.CheckConstraint('quantity > 0', name='quantity_check')

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)

    def __repr__(self):
        return '<Item %r>' % self.name

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    date_placed = db.Column( db.DateTime(), default=datetime.now)
    date_shipped = db.Column(db.DateTime())
    customer = db.relationship('Customer')

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)

    def __repr__(self):
        return '<Order %r>' % self.id

class OrderLine(db.Model):
    __tablename__ = 'orderlines'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    quantity = db.Column(db.Integer)
    order = db.relationship('Order')
    item = db.relationship('Item')

    def __init__(self, **kwargs):
        super(OrderLine, self).__init__(**kwargs)

    def __repr__(self):
        return '<OrderLine %r>' % self.quantity