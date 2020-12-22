from flask import render_template, session, redirect, url_for, current_app,request
from .. import db
from ..models import Word, Sentence, Mydict, Wheres
from . import main
from .forms import KnownForm, ImportsForm, TryingForm
from datetime import datetime
from utility.translation import get_word

@main.route('/', methods=['GET', 'POST'])
def index():
    deck=[]
    wheres = Wheres.query.group_by('wheres').all()
    for wh in wheres:
        deck.append([wh.wheres, Wheres.query.filter_by(wheres=wh.wheres).count()])
    print(deck)

    # deck = Word.query.group_by('wheres').all()
    # count = {}
    # for d in deck:
    #     count[d.where] = Word.query.filter_by(noshow=False).filter_by(where=d.where).count()
    return render_template('index.html', deck=deck)

@main.route('/study/<where>', methods=['GET', 'POST'])
def study(where):
    form = KnownForm()
    wheres = Wheres.query.filter_by(wheres=where).all()
    count = Wheres.query.filter_by(wheres=where).count()
    next_item_index = int(session.get('index'))
    while wheres[next_item_index].word.noshow and next_item_index < count-1:
        next_item_index += 1
    word = wheres[next_item_index].word
    translation = get_word(word.word)
    if form.validate_on_submit():
        if form.exit.data:
            session['index'] = 0
            return redirect(url_for('main.index'))
        word.review_timestamp = datetime.utcnow()
        word.known = bool(form.known.data)
        word.unknown = bool(form.unknown.data)
        word.blurry = bool(form.blurry.data)
        db.session.add(word)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        if form.noshow.data:
            w = Mydict(word=word.word)
            db.session.add(w)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        session['index'] = next_item_index+1
        if session['index'] >= count -1: session['index'] = count -1
        return redirect(url_for('main.study', where=where))
    return render_template('study.html', form=form, word=word,
                           translation=translation,
                           next_item_index=next_item_index)


@main.route('/updatedict', methods=['POST'])
def updatedict():
    mydict = Mydict.query.all()
    for d in mydict:
        w = Word.query.filter_by(word=d.word).first()
        if w:
            w.noshow=True
            w.noshow_timestamp=datetime.utcnow()
        else:
            w = Word(word=d.word,
                     noshow=True,
                     noshow_timestamp=datetime.utcnow()
                     )
        db.session.add(w)

    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect('/imports')

@main.route('/imports', methods=['GET', 'POST'])
def imports():
    form = ImportsForm()
    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.index'))
        return redirect(('/importdict'))
    return render_template('imports.html', form=form)


@main.route('/importdict', methods=['GET'])
def importdict():
    # Word.imports()
    # Mydict.imports()
    return redirect('/imports')

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

def get_page(myword):
    basurl='http://cn.bing.com/dict/search?q='
    searchurl=basurl+myword
    response =  urllib.request.urlopen(searchurl)
    html = response.read()
    return html