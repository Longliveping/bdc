from flask import render_template, session, redirect, url_for, current_app,request
from sqlalchemy import distinct
from .. import db
from ..models import Word, Sentence, Article, SentenceWord, WordReview, MyWord
from ..controller import show_artile_words, import_myword, import_file
from . import main
from .forms import KnownForm, ImportsForm, TryingForm, QueryForm
from datetime import datetime
from utility.translation import get_word, get_sentence
from utility.words import update_target,split_sentence
from werkzeug import secure_filename
import os


@main.route('/', methods=['GET', 'POST'])
def index():
    session['index'] = 0
    session['check'] = False
    deck = []
    articles = db.session.query(Article).all()
    for a in articles:
        words = show_artile_words(a.article)
        count = len(words)
        deck.append([a.article, count])

    return render_template('index.html', deck=deck)

@main.route('/study/<article>', methods=['GET', 'POST'])
def study(article):
    form = KnownForm()
    words = show_artile_words(article)
    count = len(words)

    if session.get('index'):
        next_item_index = min(int(session.get('index')), count-1)
    else:
        next_item_index = 0



    word = words[next_item_index]

    word_trans = ''
    sent_trans = ''
    if request.method == 'GET' :
        word_trans = get_word(word)

        if session.get('check'):
            ss = db.session.query(Sentence.sentence).join(SentenceWord).join(Word).join(Article).filter(
                Article.article == article,
                Word.word == 'part').all()
            sentences = [s[0] for s in ss]
            sents = []
            for s in sentences[:2]:
                sents.append(s)
            sents = '\n'.join(sents)
            sent_trans = get_sentence(sents,word)

    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.index'))
        if form.query.data:
            session['study'] = article
            return redirect(url_for('main.query', word=word))

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
        session['index'] = next_item_index+1
        return redirect(url_for('main.study', article=article))
    form.check.data = bool(session.get('check'))
    return render_template('study.html', form=form, word=word, translation=word_trans, sentences=sent_trans,
                           next_item_index=next_item_index)

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
            return redirect(url_for('main.study', where=session.get('study')))
        return redirect(url_for('main.query', word=form.querystring.data))
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
    import_myword()
    return redirect(url_for('main.imports'))

@main.route('/exportmyword', methods=['GET', 'POST'])
def exportdict():
    myword = db.session.query(MyWord).all()
    file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),'myword.csv')
    with open(file,'w') as f:
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
    return redirect(url_for('main.imports'))


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

