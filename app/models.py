from datetime import datetime
from . import db

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(256), unique=True)

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Article:{self.id}-{self.article}>'

class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String(256))
    translation = db.Column(db.String(256))
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
    translation = db.Column(db.String(256))

    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Word:{self.id}-{self.word}>'

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

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    noshow = db.Column(db.Boolean, default=False)
    known = db.Column(db.Boolean, default=False)
    unknown = db.Column(db.Boolean, default=True)
    blurry = db.Column(db.Boolean, default=False)
    review_timestamp = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.now())
    word = db.relationship('Word', backref='review')

    def __init__(self, **kwargs):
        super(Review, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Review:{self.id}-{self.word}>'

class Mydict(db.Model):
    __tablename__ = 'mydict'
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    word = db.relationship('Word', backref='mydict')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Mydict, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Mydict:{self.id}-{self.word}>'