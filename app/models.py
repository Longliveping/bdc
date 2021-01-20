from datetime import datetime
from . import db

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(512), unique=True)
    word_count = db.Column(db.Integer)
    sentence_count = db.Column(db.Integer)
    noshow = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Article:{self.id}-{self.article}>'

class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String(512))
    translation = db.Column(db.String(512))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    article = db.relationship('Article', backref='sentences')

    def __init__(self, **kwargs):
        super(Sentence, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Sentence:{self.id}-{self.sentence}>'

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)

    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Word:{self.id}-{self.word}>'

class Dictionary(db.Model):
    __tablename__ = 'dictionaries'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    sw = db.Column(db.String(64))
    phonetic = db.Column(db.String(64))
    definition = db.Column(db.Text)
    translation = db.Column(db.Text)
    pos = db.Column(db.String(16))
    collins = db.Column(db.Integer)
    oxford = db.Column(db.Integer)
    tag = db.Column(db.String(64))
    bnc = db.Column(db.Integer)
    frq = db.Column(db.Integer)
    exchange = db.Column(db.Text)
    detail = db.Column(db.Text)
    audio = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Dictionary, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Dictionary:{self.id}-{self.word}>'

class Lemma(db.Model):
    __tablename__ = 'lemmas'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    word = db.relationship('Word', backref='lemmas')
    lemma = db.Column(db.String(64), unique=True)

    def __init__(self, **kwargs):
        super(Lemma, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Lemma:{self.id}-{self.lemma}>'

class SentenceWord(db.Model):
    __tablename__ = 'sentencewords'
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    sentence = db.relationship('Sentence', backref='sentencewords')
    word = db.relationship('Word', backref='sentencewords')

    def __init__(self, **kwargs):
        super(SentenceWord, self).__init__(**kwargs)

    def __repr__(self):
        return f'<SentenceWord:{self.id}-{self.sentence}-{self.word}>'

class ArticleWord(db.Model):
    __tablename__ = 'articlewords'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    article = db.relationship('Article', backref='articlewords')
    word = db.relationship('Word', backref='articlewords')

    def __init__(self, **kwargs):
        super(ArticleWord, self).__init__(**kwargs)

    def __repr__(self):
        return f'<ArticleWord:{self.id}-{self.article}-{self.word}>'

class SentenceReview(db.Model):
    __tablename__ = 'sentencereviews'
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))
    noshow = db.Column(db.Boolean, default=False)
    known = db.Column(db.Boolean, default=False)
    unknown = db.Column(db.Boolean, default=True)
    blurry = db.Column(db.Boolean, default=False)
    review_timestamp = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())
    sentence = db.relationship('Sentence', backref='sentencereviews')

    def __init__(self, **kwargs):
        super(SentenceReview, self).__init__(**kwargs)

    def __repr__(self):
        return f'<SentenceReview:{self.id}-{self.sentence}>'

class WordReview(db.Model):
    __tablename__ = 'wordreviews'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    noshow = db.Column(db.Boolean, default=False)
    known = db.Column(db.Boolean, default=False)
    unknown = db.Column(db.Boolean, default=True)
    blurry = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())
    word = db.relationship('Word', backref='wordreview')

    def __init__(self, **kwargs):
        super(WordReview, self).__init__(**kwargs)

    def __repr__(self):
        return f'<WordReview:{self.id}-{self.word}>'

class MyWord(db.Model):
    __tablename__ = 'myword'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(64), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

    def __init__(self, **kwargs):
        super(MyWord, self).__init__(**kwargs)

    def __repr__(self):
        return f'<MyWord:{self.id}-{self.word}>'

class MySentence(db.Model):
    __tablename__ = 'mysentence'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String(512), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

    def __init__(self, **kwargs):
        super(MySentence, self).__init__(**kwargs)

    def __repr__(self):
        return f'<MySentence:{self.id}-{self.sentence}>'



