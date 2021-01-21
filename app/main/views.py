from flask import render_template, session, redirect, url_for, current_app,request
from sqlalchemy import distinct
from .. import db
from ..models import Word, Sentence, Article, SentenceWord, WordReview, MyWord, SentenceReview, MySentence
from ..controller import import_srt,show_artile_words,show_artile_sentences, import_myword, import_file, words_upper, update_myword
from . import main
from .forms import KnownForm, ImportsForm, TryingForm, QueryForm, SentenceKnownForm, UpdateMywordForm
from datetime import datetime
from utility.translation import get_word, get_sentence
from werkzeug import secure_filename
import os, time, re
import pyttsx3
from threading import Thread
import urllib3
import certifi
import textract
import random

def speak(sentence, rate):
    engine = pyttsx3.init()
    # print(engine.getProperty('rate'))
    # print(engine.getProperty('voice'))
    try:
        engine.setProperty('rate',int(rate))
    except:
        pass
    def onEnd():
        engine.endLoop()
    engine.connect('finished-utterance', onEnd)
    engine.say(sentence)
    try:
        engine.startLoop()
    except:
        engine.endLoop()

@main.route('/', methods=['GET', 'POST'])
def index():
    session['check'] = False
    deck = []
    articles = db.session.query(Article).all()
    for a in articles[::-1]:
        cw = a.word_count
        cs = a.sentence_count
        if not a.noshow:
            deck.append([a.article, cw, cs])

    return render_template('index.html', deck=deck)

@main.route('/study/<article>', methods=['GET', 'POST'])
def study(article):
    form = KnownForm()
    words = show_artile_words(article)
    count = len(words)
    if count == 0:
        return redirect(url_for('main.index'))

    if session.get(f'index_{article}'):
        if int(session.get(f'index_{article}')) > count-1:
            next_item_index = 0
        else:
            next_item_index = int(session.get(f'index_{article}'))
    else:
        next_item_index = 0

    if count:
        redirect(url_for('main.index'))

    word = words[next_item_index]

    word_trans = ''
    sent_trans = ''
    if request.method == 'GET' :
        word_trans = get_word(word)

        if session.get('check'):
            ss = db.session.query(Sentence.sentence).join(SentenceWord).join(Word).join(Article).filter(
                Article.article == article,
                Word.word == word).all()
            sentences = [s[0] for s in ss]
            sents = []
            for s in sentences[:2]:
                sents.append(s)
            sents = '\n'.join(sents)
            sent_trans = get_sentence(sents,word)

    if form.validate_on_submit():
        if form.exit.data:
            a = db.session.query(Article).filter(Article.article == article).first()
            a.word_count = len(show_artile_words(article))
            db.session.add(a)
            db.session.commit()
            return redirect(url_for('main.index'))
        # if form.query.data:
        #     session['study'] = article
        #     return redirect(url_for('main.query', word=word))

        session['check'] = bool(form.check.data)
        w = db.session.query(Word).filter(Word.word==word).first()
        wordreview = WordReview(word=w)
        wordreview.timestamp = datetime.utcnow()
        wordreview.known = bool(form.known.data)
        wordreview.unknown = bool(form.unknown.data)
        wordreview.blurry = bool(form.blurry.data)
        wordreview.noshow = bool(form.noshow.data)
        db.session.add(wordreview)
        db.session.commit()

        if form.noshow.data:
            mw = MyWord(word=word)
            db.session.add(mw)
            db.session.commit()

        session[f'index_{article}'] = next_item_index+1
        return redirect(url_for('main.study', article=article))
    else:
        form.check.data = bool(session.get('check'))
        return render_template('study.html', form=form, word=word, translation=word_trans, sentences=sent_trans,
                           next_item_index=next_item_index)

@main.route('/studysentence/<article>', methods=['GET', 'POST'])
def study_sentence(article):
    form = SentenceKnownForm()
    sentences = show_artile_sentences(article)
    count = len(sentences)
    if count == 0:
        return redirect(url_for('main.index'))

    if session.get(f'index_s{article}'):
        if int(session.get(f'index_s{article}')) > count-1:
            next_item_index = 0
        else:
            next_item_index = int(session.get(f'index_s{article}'))
    else:
        next_item_index = 0

    sentence = sentences[next_item_index]
    sentence = words_upper(sentence)

    sent_trans = []
    if request.method == 'GET' and session.get('show'):
        sents = [sentence]
        sents = '\n'.join(sents)
        sent_trans = get_sentence(sents.title(),'i')

    if form.validate_on_submit():
        session['show'] = bool(form.show.data)
        session['speed'] = form.speed.data
        if form.exit.data:
            a = db.session.query(Article).filter(Article.article == article).first()
            a.sentence_count = len(show_artile_sentences(article))
            db.session.add(a)
            db.session.commit()
            return redirect(url_for('main.index'))
        # if form.query.data:
        #     session['study'] = article
        #     return redirect(url_for('main.query', word='i'))
        s = db.session.query(Sentence).filter(Sentence.sentence==sentence).first()
        sentencereview = SentenceReview(sentence=s)
        sentencereview.timestamp = datetime.utcnow()
        sentencereview.known = bool(form.known.data)
        sentencereview.unknown = bool(form.unknown.data)
        sentencereview.blurry = bool(form.blurry.data)
        sentencereview.noshow = bool(form.noshow.data)
        db.session.add(sentencereview)
        db.session.commit()
        if form.repeat.data:
            return redirect(url_for('main.study_sentence', article=article))
        if form.noshow.data:
            mw = MySentence(sentence=sentence)
            db.session.add(mw)
            try:
                db.session.commit()
            except:
                pass
        session[f'index_s{article}'] = next_item_index+1
        return redirect(url_for('main.study_sentence', article=article))
    else:
        form.show.data = bool(session.get('show'))
        rate = form.speed.data = session.get('speed')
        speaker = Thread(target=speak,args=(sentence,rate,))
        speaker.start()
        return render_template('study_sentence.html', form=form, sentence=sentence, sentences=sent_trans, next_item_index=next_item_index)

@main.route('/query/<word>', methods=['GET', 'POST'])
def query(word):
    form = QueryForm()
    if not form.querystring.data:
        form.querystring.data = word
    word_trans = ''
    sent_trans = ''
    word_trans = get_word(word)
    sentences = Sentence.query.filter(Sentence.sentence.like(f'%{word}%')).limit(3).distinct()
    sents = []
    for s in sentences:
        sents.append(s.sentence)
    sents = '\n'.join(sents)
    sent_trans = get_sentence(sents,word)

    if form.validate_on_submit():
        if form.exit.data:
            # return redirect(url_for('main.study', where=session.get('study')))
            return redirect(url_for('main.index'))
    else:
        return render_template('query.html', form=form, word=word,
                           translation=word_trans, sentences=sent_trans)

@main.route('/imports', methods=['GET', 'POST'])
def imports():
    form = ImportsForm()
    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.index'))
        if form.importfolder.data:
            return redirect(url_for('main.importfolder'))

    return render_template('imports.html', form=form)

@main.route('/importmyword', methods=['GET', 'POST'])
def importmyword():
    file = os.path.join(current_app.config.get('MYWORD_FOLDER'), 'import/myword.txt')
    session['upload_file'] = file
    return redirect(url_for('main.updatemyword'))

@main.route('/exportmyword', methods=['GET', 'POST'])
def exportmyword():
    myword = db.session.query(MyWord).all()
    file = os.path.join(current_app.config.get('MYWORD_FOLDER'),'export/myword.txt')
    with open(file,'w+') as f:
        for w in myword:
            f.write(w.word+'\n')
    return redirect(url_for('main.imports'))

@main.route('/importfolder', methods=['GET'])
def importfolder():
    return redirect(url_for('main.imports'))

@main.route('/importfile', methods=['POST'])
def importfile():
    f = request.files['filename']
    file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),secure_filename(f.filename))
    f.save(file)
    import_file(file)
    session['upload_file'] = file
    return redirect(url_for('main.updatemyword'))

@main.route('/importsrt', methods=['POST'])
def importsrt():
    f = request.files['filename']
    file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),secure_filename(f.filename))
    f.save(file)
    import_srt(file)
    session['upload_file'] = file
    return redirect(url_for('main.updatemyword'))

@main.route('/importurl', methods=['POST'])
def importurl():
    url = request.form["url"]

    http = urllib3.contrib.socks.SOCKSProxyManager('socks5h://localhost:12345',ca_certs=certifi.where())
    try:
        req = http.request('GET', url)
        filename = secure_filename(url.split('/')[-1])
        if not filename:
            filename = secure_filename(url.split('/')[-2])
        filename = re.sub(r'[^\w_\-]','',filename)[:25]
        filename = filename + str(random.randrange(1000,10000))
        htmlfile = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.html")
        with open(htmlfile, 'wb') as f:
            f.write(req.data)
        text = textract.process(htmlfile)
        file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.txt")
        with open(file,'wb') as f:
            f.write(text)
        import_file(file)
        session['upload_file'] = file
        return redirect(url_for('main.updatemyword'))
    except:
        return redirect(url_for('main.imports'))


@main.route('/updatemyword', methods=['GET', 'POST'])
def updatemyword():
    form = UpdateMywordForm()
    (un_known, known) = update_myword(session.get('upload_file'))
    choices = un_known + known
    choice = [(id, value) for id,value in enumerate(choices)]
    form.choices.choices = choice

    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.imports'))
        current_app.logger.debug(form.choices.data)
        sourcedir = current_app.config.get('MYWORD_FOLDER')
        file = os.path.join(sourcedir, 'import/myword.txt' )
        with open(file, 'w') as f:
            for c in choice:
                if c[0] in form.choices.data:
                    f.write(c[1]+'\n')
        file = os.path.join(sourcedir, 'import/remove.txt' )
        with open(file, 'w') as f:
            for c in choice:
                if c[0] not in form.choices.data:
                    f.write(c[1]+'\n')
        import_myword()
        return redirect(url_for('main.updatemyword'))
    else:
        form.choices.data = [len(un_known)+id for id,value in enumerate(known)]
        return render_template('updatemyword.html', form=form)

@main.route('/trying', methods=['GET', 'POST'])
def trying():
    form = TryingForm()
    if form.validate_on_submit():
        if form.exit.data:
            session['index'] = 0
            return redirect(url_for('main.index'))
        session['index'] = int(form.index.data)+1
        session['check'] = bool(form.check.data)
        return redirect(url_for('main.trying'))
    form.index.data = session.get('index')
    form.check.data = bool(session.get('check'))
    return render_template('trying.html', form=form)

