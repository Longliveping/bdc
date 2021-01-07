from datetime import datetime
from . import db

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(512), unique=True)

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
    word = db.Column(db.String(256), unique=True)
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
    review_timestamp = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.now())
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow,onupdate=datetime.now())
    word = db.relationship('Word', backref='wordreview')

    def __init__(self, **kwargs):
        super(WordReview, self).__init__(**kwargs)

    def __repr__(self):
        return f'<WordReview:{self.id}-{self.word}>'

class MyWord(db.Model):
    __tablename__ = 'myword'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(256), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(MyWord, self).__init__(**kwargs)

    def __repr__(self):
        return f'<MyWord:{self.id}-{self.word}>'

class MySentence(db.Model):
    __tablename__ = 'mysentence'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String(512), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(MySentence, self).__init__(**kwargs)

    def __repr__(self):
        return f'<MySentence:{self.id}-{self.sentence}>'



