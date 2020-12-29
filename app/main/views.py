from flask import render_template, session, redirect, url_for, current_app,request
from .. import db
from ..models import Word, Sentence, Mydict, Wheres, db_update_record
from . import main
from .forms import KnownForm, ImportsForm, TryingForm, QueryForm
from datetime import datetime
<<<<<<< HEAD
from utility.translation import get_word, get_sentence
from utility.words import update_target,split_sentence
from werkzeug import secure_filename
import os

=======
from utility.translation import get_word
from werkzeug import secure_filename
import os
>>>>>>> update with sentence

@main.route('/', methods=['GET', 'POST'])
def index():
    deck=[]
    wheres = Wheres.query.group_by('wheres').all()
    for wh in wheres:
        deck.append([wh.wheres, Wheres.query.filter_by(wheres=wh.wheres).count()])
    return render_template('index.html', deck=deck)

@main.route('/study/<where>', methods=['GET', 'POST'])
def study(where):
    form = KnownForm()
    wheres = Wheres.query.filter_by(wheres=where).all()
    count = Wheres.query.filter_by(wheres=where).count()
    if session.get('index'):
        next_item_index = int(session.get('index'))
    else:
        next_item_index = 0
    if session.get('noshow'):
        noshow_count = int(session.get('noshow'))
    else:
        noshow_count = 0
    while wheres[next_item_index].word.noshow and next_item_index < count-1:
        next_item_index += 1
    word = wheres[next_item_index].word
<<<<<<< HEAD
    word_trans = ''
    sent_trans = ''
    if request.method == 'GET':
        word_trans = get_word(word.word)
        sentences = Sentence.query.filter(Sentence.wheres.like(f'%{where}%')).filter(Sentence.sentence.like(f'%{word.word}%')).limit(3).distinct()
        sents = []
        for s in sentences:
            sents.append(s.sentence)
        sents = '\n'.join(sents)
        sent_trans = get_sentence(sents,word.word)

    if form.validate_on_submit():
        if form.exit.data:
            Word.update_noshow(noshow_count)
            session['noshow'] = 0
=======
    translation = get_word(word.word)
    sentences = Sentence.query.filter(Sentence.wheres.like(f'%{where}%')).filter(Sentence.sentence.like(f'%{word.word}%')).distinct()
    print(word.wheres)
    if form.validate_on_submit():
        if form.exit.data:
            Word.updatebymydict()
>>>>>>> update with sentence
            session['index'] = 0
            return redirect(url_for('main.index'))
        if form.query.data:
            session['study'] = where
            return redirect(url_for('main.query', word=word.word))
        word.review_timestamp = datetime.utcnow()
        word.known = bool(form.known.data)
        word.unknown = bool(form.unknown.data)
        word.blurry = bool(form.blurry.data)
        db_update_record(word)
        if form.noshow.data:
            w = Mydict(word=word.word)
            db_update_record(w)
            noshow_count += 1
            session['noshow'] = noshow_count
        session['index'] = next_item_index+1
        if session['index'] >= count -1: session['index'] = count -1
        return redirect(url_for('main.study', where=where))
    return render_template('study.html', form=form, word=word,
<<<<<<< HEAD
                           translation=word_trans, sentences=sent_trans,
                           next_item_index=next_item_index)

@main.route('/query/<word>', methods=['GET', 'POST'])
def query(word):
    form = QueryForm()
    if not form.querystring.data:
        form.querystring.data = word
    word_trans = ''
    sent_trans = ''
    word_trans = get_word(word)
    sentences = Sentence.query.filter(Sentence.sentence.like(f'%{word}%')).limit(5).distinct()
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

=======
                           translation=translation, sentences = sentences,
                           next_item_index=next_item_index)

>>>>>>> update with sentence
@main.route('/imports', methods=['GET', 'POST'])
def imports():
    form = ImportsForm()
    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.index'))
        if form.importfolder.data:
            return redirect(url_for('main.importfolder'))
    return render_template('imports.html', form=form)

@main.route('/importdict', methods=['GET', 'POST'])
def importdict():
    Mydict.imports()
    return redirect(url_for('main.imports'))

<<<<<<< HEAD
@main.route('/exportdict', methods=['GET', 'POST'])
def exportdict():
    dict = Mydict.query.all()
    app = current_app._get_current_object()
    file = os.path.join(app.config['UPLOAD_FOLDER'],'mydict.csv')
    with open(file,'w') as f:
        for d in dict:
            f.write(d.word+'\n')
    return redirect(url_for('main.imports'))

@main.route('/importfolder', methods=['GET'])
def importfolder():
    Word.imports()
=======
@main.route('/importfolder', methods=['GET'])
def importfolder():
    # Word.imports()
    print('import folder')
>>>>>>> update with sentence
    return redirect(url_for('main.imports'))

@main.route('/importfile', methods=['POST'])
def importfile():
    app = current_app._get_current_object()
    f = request.files['filename']
    filename = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
    f.save(filename)
    Word.importfile(filename)
    return redirect(url_for('main.imports'))

@main.route('/importsentence', methods=['POST'])
def importsentence():
    app = current_app._get_current_object()
    f = request.files['filename']
    filename = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename))
    f.save(filename)
    Sentence.importfile(filename)
    return redirect(url_for('main.imports'))

@main.route('/trying', methods=['GET', 'POST'])
def trying():
    form = TryingForm()
    if form.validate_on_submit():
        if form.exit.data:
            session['index'] = 0
            return redirect(url_for('main.index'))
        session['index'] = int(form.index.data)+1
        return redirect(url_for('main.trying'))
    form.index.data = session.get('index')
    return render_template('trying.html', form=form)

