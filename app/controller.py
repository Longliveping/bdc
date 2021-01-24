from flask import current_app, request
from app import create_app, db
from app.models import Word, Lemma,Dictionary, Article, Sentence, SentenceWord, ArticleWord, SentenceReview, WordReview, MyWord, MySentence
import os
from utility.words import my_word, LemmaDB, get_token, Timer


def db_init_word():
    with Timer() as timer:
        sourcedir = current_app.config.get('MYWORD_FOLDER')
        file = os.path.join(sourcedir, 'import/lemma.en.txt' )
        lemma = LemmaDB()
        lemma.load(file)
        data = lemma.get_stems()
        for d in data:
            w = Word(word=d[1], frequency=d[0])
            db.session.add(w)
            for x in d[2].split(','):
                l = Lemma(word=w, lemma=x)
                db.session.add(l)
        db.session.commit()
    print("took", timer.duration, "seconds")

def show_artile_words(article_name):
    myword = db.session.query(MyWord.word).all()
    mywords = set([w[0] for w in myword])

    article_word = db.session.query(Word.word).join(ArticleWord).join(Article).filter(
        Article.article == article_name,
        Word.word.notin_(mywords)
    ).order_by(Word.id).all()

    article_words = [w[0] for w in article_word]
    return article_words

def show_artile_sentences(article_name):
    mysentence = db.session.query(MySentence.sentence).all()
    mysentences = set([w[0] for w in mysentence])

    article_sentence = db.session.query(Sentence.sentence).join(Article).filter(
        Article.article == article_name,
        Sentence.sentence.notin_(mysentences)
    ).order_by(Sentence.id).all()

    article_sentences = [w[0] for w in article_sentence]
    return article_sentences

def show_my_words():
    myword = db.session.query(MyWord.word).all()
    mywords = set([w[0] for w in myword])
    return mywords

def words_upper(sentence):
    mywords = show_my_words()
    sw = set(get_token(sentence))
    words = sw - mywords
    for w in words:
        sentence = sentence.replace(w, w.upper())
    return sentence
