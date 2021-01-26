from flask import render_template, session, redirect, url_for, current_app,request
from .. import db
from ..models import Word, Sentence, Article, SentenceWord, WordReview, MyWord, SentenceReview, MySentence
from . import main
from .forms import WordKnownForm, ImportsForm, TryingForm, QueryForm, \
    SentenceKnownForm, UpdateMywordForm, UpdateTextForm, UpdateArticleShowForm
from datetime import datetime
from utility.translation import get_word, get_sentence
from werkzeug import secure_filename
import os, re
from threading import Thread
import urllib3
import certifi
import textract
from utility.words import article_file, my_word, get_token, articles, \
    aritcle_sentence, speak, words_upper, article_word


@main.route('/', methods=['GET', 'POST'])
def index():
    deck = []
    articles = db.session.query(Article).all()
    for a in articles[::-1]:
        if not a.noshow:
            article_word.load(a.article)
            aritcle_sentence.load(a.article)
            deck.append([a.article, article_word.get_new_word_count(), article_word.get_favorite_word_count(),
                         aritcle_sentence.get_sentence_count(), aritcle_sentence.get_favorite_sentence_count()])

    return render_template('index.html', deck=deck)

@main.route('/studyword/<article>/<type>', methods=['GET', 'POST'])
def study_word(article, type):
    form = WordKnownForm()
    article_word.load(article)
    if type == 'new':
        words = article_word.get_new_word()
        count = article_word.get_new_word_count()
    else:
        words = article_word.get_favorite_word()
        count = article_word.get_favorite_word_count()

    if count == 0:
        return redirect(url_for('main.index'))

    if session.get(f'index_{article}'):
        if int(session.get(f'index_{article}')) > count-1:
            next_item_index = 0
        else:
            next_item_index = int(session.get(f'index_{article}'))
    else:
        next_item_index = 0

    word = words[next_item_index]

    if form.validate_on_submit():
        if form.exit.data:
            a = db.session.query(Article).filter(Article.article == article).first()
            a.word_count = article_word.get_new_word_count()
            db.session.add(a)
            db.session.commit()
            return redirect(url_for('main.index'))
        # if form.query.data:
        #     session['study'] = article
        #     return redirect(url_for('main.query', word=word))

        session['show_wordsentence'] = bool(form.show_sentence.data)
        session['show_wordtranslaiton'] = bool(form.show_translation.data)
        w = db.session.query(Word).filter(Word.word==word).first()
        wordreview = WordReview(word=w)
        wordreview.timestamp = datetime.utcnow()
        wordreview.known = bool(form.favorite.data)
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
        return redirect(url_for('main.study_word', article=article, type=type))
    else:
        sent_trans = ''
        word_trans = get_word(word)
        if not session.get('show_wordtranslaiton'):
            word_trans['chinese'] = []
        if session.get('show_wordsentence'):
            ss = db.session.query(Sentence.sentence).join(SentenceWord).join(Word).join(Article).filter(
                Article.article == article,
                Word.word == word).all()
            sentences = [s[0] for s in ss]
            sents = []
            for s in sentences[:2]:
                sents.append(s)
            sents = '\n'.join(sents)
            sent_trans = get_sentence(sents,word)
        form.show_sentence.data = bool(session.get('show_wordsentence'))
        form.show_translation.data = bool(session.get('show_wordtranslaiton'))
        return render_template('study_word.html',
                               form=form,
                               word=word,
                               translation=word_trans,
                               sentences=sent_trans,
                               next_item_index=next_item_index)

@main.route('/studysentence/<article>/<type>', methods=['GET', 'POST'])
def study_sentence(article, type):
    form = SentenceKnownForm()
    aritcle_sentence.load(article)
    if type == 'new':
        sentences_id = aritcle_sentence.get_sentence_id()
        sentences = aritcle_sentence.get_sentence()
        meanings = aritcle_sentence.get_translation()
        count = aritcle_sentence.get_sentence_count()
    else:
        sentences_id = aritcle_sentence.get_favorite_sentence_id()
        sentences = aritcle_sentence.get_favorite_sentence()
        meanings = aritcle_sentence.get_favorite_translation()
        count = aritcle_sentence.get_favorite_sentence_count()

    if count == 0:
        return redirect(url_for('main.index'))

    if session.get(f'index_s{article}'):
        if int(session.get(f'index_s{article}')) > count-1:
            next_item_index = 0
        else:
            next_item_index = int(session.get(f'index_s{article}'))
    else:
        next_item_index = 0

    sentence_id = sentences_id[next_item_index]
    sentence = sentences[next_item_index]
    sentence = words_upper(sentence)
    meaning = meanings[next_item_index]

    if form.validate_on_submit():
        session['show_translation'] = bool(form.show_translation.data)
        session['show_meaning'] = bool(form.show_meaning.data)
        session['show_sentence'] = bool(form.show_sentence.data)
        session['speed'] = form.speed.data
        if form.exit.data:
            a = db.session.query(Article).filter(Article.article == article).first()
            a.sentence_count = aritcle_sentence.get_sentence_count()
            db.session.add(a)
            db.session.commit()
            return redirect(url_for('main.index'))
        # if form.query.data:
        #     session['study'] = article
        #     return redirect(url_for('main.query', word='i'))
        s = db.session.query(Sentence).filter(Sentence.id == sentence_id).first()
        sentencereview = SentenceReview(sentence=s)
        sentencereview.timestamp = datetime.utcnow()
        sentencereview.known = bool(form.favoriate.data)
        sentencereview.unknown = bool(form.unknown.data)
        sentencereview.blurry = bool(form.blurry.data)
        sentencereview.noshow = bool(form.noshow.data)
        db.session.add(sentencereview)
        db.session.commit()
        if form.repeat.data:
            return redirect(url_for('main.study_sentence', article=article, type=type))
        if form.noshow.data:
            mw = MySentence(sentence=sentence)
            db.session.add(mw)
            try:
                db.session.commit()
            except:
                pass
        session[f'index_s{article}'] = next_item_index+1
        return redirect(url_for('main.study_sentence', article=article, type=type))
    else:
        if not bool(session.get('show_meaning')):
            meaning = ''
        if not bool(session.get('show_sentence')):
            sentence = ''
        sent_trans = []
        if bool(session.get('show_sentence')) and session.get('show_translation'):
            sents = [sentence]
            sents = '\n'.join(sents)
            sent_trans = get_sentence(sents.title(),'i')
        form.show_translation.data = bool(session.get('show_translation'))
        form.show_meaning.data = bool(session.get('show_meaning'))
        form.show_sentence.data = bool(session.get('show_sentence'))
        rate = form.speed.data = session.get('speed')
        speaker = Thread(target=speak,args=(sentence,rate,))
        speaker.start()
        return render_template('study_sentence.html', form=form, sentence=sentence, meaning=meaning, sentence_translation=sent_trans, next_item_index=next_item_index)

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
    # extract_text(file)
    # session['upload_file'] = file
    # article_file()
    with open(file,'r') as f:
        my_word.add_myword(get_token(f.read()))
    return redirect(url_for('main.imports'))

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
    article_file.load(file)
    return redirect(url_for('main.updatetext'))

@main.route('/updatearticleshow', methods=['GET', 'POST'])
def updatearticleshow():
    form = UpdateArticleShowForm()
    articles.get_articles()
    (un_known, known) = articles.diff_noshow()
    choices = un_known + known
    choice = [(id, value) for id,value in enumerate(choices)]
    form.choices.choices = choice

    if form.validate_on_submit():
        show = []
        no_show = []
        for c in choice:
            if c[0] in form.choices.data:
                show.append(c[1])
            else:
                no_show.append(c[1])
        articles.set_noshow(show, no_show)
        return redirect(url_for('main.index'))
    else:
        form.choices.data = [len(un_known)+id for id,value in enumerate(known)]
        return render_template('articleshow.html', form=form)

@main.route('/importurl', methods=['POST'])
def importurl():
    url = request.form["url"]
    http = urllib3.contrib.socks.SOCKSProxyManager('socks5h://localhost:12345',ca_certs=certifi.where())
    try:
        req = http.request('GET', url)
        filename = secure_filename(url.split('/')[-1])
        if not filename:
            filename = secure_filename(url.split('/')[-2])
        filename = re.sub(r'[^\w_\-]','',filename)[:50]
        htmlfile = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.html")
        with open(htmlfile, 'wb') as f:
            f.write(req.data)
        text = textract.process(htmlfile)
        file = os.path.join(current_app.config.get('UPLOAD_FOLDER'),f"{filename}.txt")
        with open(file,'wb') as f:
            f.write(text)
        article_file.load(file)
        return redirect(url_for('main.updatetext'))
    except:
        return redirect(url_for('main.imports'))

@main.route('/updatetext', methods=['GET', 'POST'])
def updatetext():
    form = UpdateTextForm()
    if form.validate_on_submit():
        article_file.set_filename(form.title.data)
        article_file.update_text(form.text.data)
        article_file.import_file()
        return redirect(url_for('main.updatemyword'))
    else:
        form.title.data = article_file.get_filename()
        form.text.data = article_file.get_text()
        return render_template('updatetext.html', form=form)

@main.route('/updatemyword', methods=['GET', 'POST'])
def updatemyword():
    form = UpdateMywordForm()
    (un_known, known) = my_word.diff_myword(article_file.get_token())
    choices = un_known + known
    choice = [(id, value) for id,value in enumerate(choices)]
    form.choices.choices = choice

    if form.validate_on_submit():
        if form.exit.data:
            return redirect(url_for('main.imports'))
        add_word = []
        rm_word = []
        for c in choice:
            if c[0] in form.choices.data:
                add_word.append(c[1])
            else:
                rm_word.append(c[1])

        my_word.add_myword(add_word)
        my_word.rm_myword(rm_word)
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

