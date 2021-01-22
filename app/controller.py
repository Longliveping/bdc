import unittest
from flask import current_app, request
from app import create_app, db
from app.models import Word, Lemma,Dictionary, Article, Sentence, SentenceWord, ArticleWord, SentenceReview, WordReview, MyWord, MySentence
import os
import re
import time
from datetime import datetime
from werkzeug import secure_filename
import urllib3
import certifi
import textract
import random
from utility.words import create_sentence_srt_json,read_word_by_file,  \
    get_token,get_valid_token, \
    read_text, read_file_by_name, extract_text,extract_srt,  \
    read_sentence_json_file,  \
    create_sentence_english_json, _create_word_json, read_word_json_file, LemmaDB, \
    read_word, read_sentence, read_valid_word_from_file, read_sentence_by_filename, read_word_by_filename


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, value, tb):
        self.duration = time.time() - self.start


def import_article(filename):
    basename = os.path.basename(read_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(Article).filter(Article.article == filename).first()
    if not a:
        a1 = Article(article=filename, word_count=0, sentence_count=0)
        db.session.add(a1)
        db.session.commit()

def import_word(filename):
    with Timer() as timer:
        tokens = set(read_word(read_word_json_file(filename)))
        exist = db.session.query(Word.word).all()
        exists =  set([e[0] for e in exist])
        not_exist = tokens - exists
        for n in not_exist:
            w = Word(word=n)
            db.session.add(w)
        db.session.commit()
    print("took", timer.duration, "seconds")

def import_sentence(filename):
    basename = os.path.basename(read_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(Sentence).join(Article).filter(Article.article == filename).first()
    if a:
        return

    with Timer() as timer:
        # insert SentenceWords
        db.session.remove()
        article = db.session.query(Article).filter(Article.article == filename).first()

        sl = []
        sentences = read_sentence_by_filename(filename)
        tokens_all = set(read_word_by_filename(filename))

        words_all = db.session.query(Word).filter(Word.word.in_(tokens_all)).all()
        for sentence,_ in sentences.items():
            tokens = get_token(sentence)
            s = Sentence(sentence=sentence, article=article)
            w = [w for w in words_all if w.word in tokens]
            sw = [SentenceWord(word=i) for i in w]
            s.sentencewords = sw
            sl.append(s)
        db.session.add_all(sl)
        db.session.commit()

    print("import sentence took", timer.duration, "seconds")

def update_article_count(filename):
    basename = os.path.basename(read_file_by_name(filename))
    filename = basename.split('.')[0]
    article = db.session.query(Article).filter(Article.article == filename).first()
    article.sentence_count = len(show_artile_sentences(filename))
    article.word_count = len(show_artile_words(filename))
    db.session.add(article)
    db.session.commit()

def import_sentence_srt(filename):
    basename = os.path.basename(read_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(Sentence).join(Article).filter(Article.article == filename).first()
    if a:
        return

    with Timer() as timer:
        # insert SentenceWords
        db.session.remove()
        article = db.session.query(Article).filter(Article.article == filename).first()

        sl = []
        sentences = read_sentence(read_sentence_json_file(filename))
        tokens_all = set(read_word(read_word_json_file(filename)))

        words_all = db.session.query(Word).filter(Word.word.in_(tokens_all)).all()
        for sen,trans in sentences.items():
            tokens = get_token(sen)
            s = Sentence(sentence=sen, translation=trans,article=article)
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
        file = os.path.join(sourcedir, 'import/myword.txt' )
        tokens = set(read_valid_word_from_file(file))
        exist = db.session.query(MyWord.word).all()
        exists = set([e[0] for e in exist])
        not_exists = tokens - exists
        for t in not_exists:
            m = MyWord(word=t)
            db.session.add(m)
        db.session.commit()

        file = os.path.join(sourcedir, 'import/remove.txt' )
        remove_tokens = set(read_word_by_file((file)))
        if remove_tokens:
            db.session.query(MyWord).filter(MyWord.word.in_(remove_tokens)).delete(synchronize_session='fetch')
            db.session.commit()
    print("took", timer.duration, "seconds")

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

def db_init_myword():
    with Timer() as timer:
        sourcedir = current_app.config.get('MYWORD_FOLDER')
        file = os.path.join(sourcedir, 'import/myword.txt' )
        tokens = set(read_valid_word_from_file(file))
        db.session.query(MyWord).delete(synchronize_session='fetch')
        db.session.commit()
        for t in tokens:
            w = MyWord(word=t)
            db.session.add(w)
        db.session.commit()
    print("db_init_myword took", timer.duration, "seconds")


def import_lemma():
    with Timer() as timer:
        sourcedir = current_app.config.get('MYWORD_FOLDER')
        file = os.path.join(sourcedir, 'import/myword.txt' )
        tokens = set(read_word_by_file((file)))
        exist = db.session.query(MyWord.word).all()
        exists = set([e[0] for e in exist])
        not_exists = tokens - exists
        for t in not_exists:
            m = MyWord(word=t)
            db.session.add(m)
        db.session.commit()

        file = os.path.join(sourcedir, 'import/remove.txt' )
        remove_tokens = set(read_word_by_file((file)))
        db.session.query(MyWord).filter(MyWord.word.in_(remove_tokens)).delete(synchronize_session='fetch')
        db.session.commit()
    print("took", timer.duration, "seconds")

def import_articleword(filename):
    basename = os.path.basename(read_file_by_name(filename))
    filename = basename.split('.')[0]
    a = db.session.query(ArticleWord).join(Article).filter(Article.article == filename).first()
    if a:
        return

    with Timer() as timer:
        # insert ArticleWords
        db.session.remove()
        article = db.session.query(Article).filter(Article.article == filename).first()
        tokens = set(read_word_by_filename(filename))
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
    sw = set(get_valid_token(sentence))
    words = sw - mywords
    for w in words:
        sentence = sentence.replace(w, w.upper())
    return sentence

def import_file(file):
    extract_text(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    import_article(filename)
    import_sentence(filename)
    import_articleword(filename)
    update_article_count(filename)

def import_srt(file):
    extract_srt(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    import_article(filename)
    import_sentence_srt(filename)
    import_articleword(filename)
    update_article_count(filename)


def update_myword(file):
    # basename = os.path.basename(file)
    # filename = basename.split('.')[0]
    tokens = set(read_word(file))
    myword = db.session.query(MyWord.word).all()
    mywords = set([w[0] for w in myword])
    un_known = tokens - mywords
    known = tokens - un_known
    return (list(un_known), list(known))

def import_url(url):
    http = urllib3.contrib.socks.SOCKSProxyManager('socks5h://localhost:12345',ca_certs=certifi.where())
    try:
        req = http.request('GET', url)
        filename = secure_filename(url.split('/')[-1])
        if not filename:
            filename = secure_filename(url.split('/')[-2])
        filename = re.sub(r'[^\w_\-]','',filename)[:25]
        filename = filename + str(random.randrange(0,256))
        htmlfile = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.html")
        with open(htmlfile, 'wb') as f:
            f.write(req.data)
        text = textract.process(htmlfile)
        file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.txt")
        with open(file,'wb') as f:
            f.write(text)
        import_file(file)
    except:
        pass
