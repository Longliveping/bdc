import re
import PyPDF2 as pdf
import os, sys, time
import docx
# from app.controller import show_artile_words
from app.models import db, Word, Lemma, MyWord, Article,\
    ArticleWord,Dictionary,SentenceWord,Sentence,SentenceReview,MySentence, WordReview
from sqlalchemy import or_, distinct
import pyttsx3
from werkzeug import secure_filename

class My_Word(object):

    def __init__(self):
        self._myword = []
        self._addword = []
        self._rmword = []

    def add_myword(self, word):
        words = set(word)
        token = db.session.query(Word.word).join(Lemma).filter(or_(
            Lemma.lemma.in_(words),
            Word.word.in_(words)
        )).all()
        tokens = set([e[0] for e in token])
        exist = db.session.query(MyWord.word).all()
        exists = set([e[0] for e in exist])
        not_exists = set(tokens) - exists
        self._addword = not_exists
        self._add_myword()

    def rm_myword(self, word):
        self._rmword = word
        self._rm_myword()

    def get_myword(self):
        if not self._myword:
            myword = db.session.query(MyWord.word).all()
            self._myowrd = [w[0] for w in myword]
        return self._myowrd

    def _add_myword(self):
        for a in self._addword:
            m = MyWord(word=a)
            db.session.add(m)
        db.session.commit()

    def _rm_myword(self):
        db.session.query(MyWord).filter(MyWord.word.in_(self._rmword)).delete(synchronize_session='fetch')
        db.session.commit()

    def diff_myword(self, token=()):
        if token:
            tokens = set(token)
            mywords = set(self.get_myword())
            un_known = tokens - mywords
            known = tokens - un_known
        else:
            un_known = ()
            known = self._addword
        return (list(un_known), list(known))


class Article_File(object):

    def __init__(self):
        self._file = None
        self._article = None
        self._dirname = None
        self._basename = None
        self._filename = None
        self._file_extension = None
        self._text = ''
        self._token = []
        self._words_all = {}
        self._sentence = {}
        self._word = {}

    def load(self, file):
        if file:
            self._file = file
            self._dirname = os.path.dirname(file)
            self._basename = os.path.basename(file)
            self._filename = self._basename.split('.')[0]
            self._file_extension = self._basename.split('.')[1]
            self._extract_text()


    def get_sentence(self):
        return self._sentence

    def get_word(self):
        return self._word

    def get_token(self):
        return self._token

    def get_text(self):
        return self._text

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        self._filename = secure_filename(filename)

    def _extract_text(self):
        if self._allowed_file_extenstion():
            fullText = []
            if self._file_extension == ('txt'):
                with open(self._file, 'r') as f:
                    fullText = f.readlines()
            elif self._file_extension == 'pdf':
                with open(self._file, 'rb') as f:
                    pdfReader = pdf.PdfFileReader(f)
                    for pagenumber in range(pdfReader.numPages):
                        pageObj = pdfReader.getPage(pagenumber)
                        fullText.append(pageObj.extractText().lower())
            elif self._file_extension == 'docx':
                doc = docx.Document(self._file)
                for para in doc.paragraphs:
                    fullText.append(para.text)

            fullText = '\n'.join(fullText)
            pttn = re.compile(r'([A-Za-z]+.*?[\.\?\!\n])', re.M)
            lines = re.findall(pttn,fullText)
            lines = [re.sub(r'\n','',x) for x in lines]

            fullText = '\n'.join(lines)
            self._text = fullText

            if self._file_extension == 'srt':
                with open(self._file, 'r', encoding='utf8') as f:
                    fullText = f.read()
                pttn = re.compile(r'\d{1,4}\n.*\n(.*)\n(.*)\n', re.M)
                lines = re.findall(pttn,fullText)
                json_sentences = {}
                for count in range(len(lines)):
                    key = re.sub(r'^[^\w]*','',lines[count][1])
                    value = re.sub(r'[^\u4e00-\u9fa5]*','',lines[count][0])
                    if re.match(r'^[A-Za-z]', key):
                        json_sentences[key] = value

                sentence_list = [f'{key} ::: {value}' for key, value in json_sentences.items()]
                sentence_list = '\n'.join(sentence_list)
                self._text = sentence_list

    def _get_word_all(self):
        words = db.session.query(Word).filter(Word.word.in_(self._token)).all()
        for w in words:
            self._words_all[w.word] = w

    def _get_article(self):
        self._article = db.session.query(Article).filter(Article.article == self._filename).first()

    def update_text(self, text):
        fullText = text
        pttn = re.compile(r'([A-Za-z]+.*?[\.\?\!\n])', re.M)
        lines = re.findall(pttn,fullText)
        lines = [re.sub(r'\n','',x) for x in lines]
        self._text = '\n'.join(lines)

        if self._file_extension == 'srt':
            for line in lines:
                key = line.split(':::')[0]
                value = line.split(':::')[1]
                self._sentence[key] = value
        else:
            lines = [re.sub(r'\n','',x) for x in lines]
            for line in lines:
                self._sentence[line] = '1'

        self._token = self._get_valid_token(self._text)
        for count in range(len(self._token)):
            self._word[self._token[count].strip()] = 1

    def _allowed_file_extenstion(self):
        EXTENSIONS = {'txt','srt', 'pdf', 'docx'}
        if self._file_extension in EXTENSIONS:
            return True
        else:
            return False

    def _get_valid_token(self, text):
        with Timer() as timer:
            tokens = re.findall('[a-z]+', text.lower())
            tokens = set(list(dict.fromkeys(tokens)))
            tokens = db.session.query(Word.word).join(Lemma).filter(or_(
                Lemma.lemma.in_(tokens),
                Word.word.in_(tokens)
            )).all()
            tokens = list(set([x[0] for x in tokens]))
        print('get valid token took', timer.duration, 'seconds')
        return tokens

    def import_file(self):
        self._import_article()
        self._import_sentence()
        self._import_articleword()
        self._update_article_count()

    def _import_article(self):
        a = db.session.query(Article).filter(Article.article == self._filename).first()
        if not a:
            a1 = Article(article=self._filename, word_count=0, sentence_count=0)
            db.session.add(a1)
            db.session.commit()

    def _import_sentence(self):
        a = db.session.query(Sentence).join(Article).filter(Article.article == self._filename).first()
        if a:
            return

        with Timer() as timer:
            # insert SentenceWords
            db.session.remove()
            self._get_word_all()
            self._get_article()
            sl = []
            for sentence, translation in self._sentence.items():
                if self._file_extension == 'srt':
                    s = Sentence(sentence=sentence,translation=translation, article=self._article)
                else:
                    s = Sentence(sentence=sentence, article=self._article)

                w = [self._words_all[t] for t in get_token(sentence) if t in self._token]
                sw = [SentenceWord(word=i) for i in w]
                s.sentencewords = sw
                sl.append(s)
                db.session.add_all(sl)
            db.session.commit()

        print("import sentence took", timer.duration, "seconds")

    def _import_articleword(self):
        a = db.session.query(ArticleWord).join(Article).filter(Article.article == self._filename).first()
        if a:
            return

        with Timer() as timer:
            # insert ArticleWords
            db.session.remove()
            article = db.session.query(Article).filter(Article.article == self._filename).first()
            words = db.session.query(Word).filter(Word.word.in_(self._token)).all()
            aw = [ArticleWord(article=article, word=w) for w in words]
            db.session.add_all(aw)
            db.session.commit()
        print("took", timer.duration, "seconds")

    def _update_article_count(self):
        article = db.session.query(Article).filter(Article.article == self._filename).first()
        article.sentence_count = len(self._show_artile_sentences())
        article.word_count = len(self._show_artile_words())
        db.session.add(article)
        db.session.commit()

    def _show_artile_words(self):
        myword = db.session.query(MyWord.word).all()
        mywords = set([w[0] for w in myword])

        article_word = db.session.query(Word.word).join(ArticleWord).join(Article).filter(
            Article.article == self._filename,
            Word.word.notin_(mywords)
        ).order_by(Word.id).all()

        article_words = [w[0] for w in article_word]
        return article_words

    def _show_artile_sentences(self):
        mysentence = db.session.query(MySentence.sentence).all()
        mysentences = set([w[0] for w in mysentence])

        article_sentence = db.session.query(Sentence.sentence).join(Article).filter(
            Article.article == self._filename,
            Sentence.sentence.notin_(mysentences)
        ).order_by(Sentence.id).all()

        article_sentences = [w[0] for w in article_sentence]
        return article_sentences


class Article_s(object):

    def __init__(self):
        self._articles = []
        self._articlename = {}
        self._show = {}
        self._noshow = {}
        self._wordcount = {}


    def get_articles(self):
        articles = db.session.query(Article).all()
        self._articles = articles
        for a in articles:
            self._articlename[a.id] = a.article
            self._noshow[a.article] = a.noshow
            self._wordcount[a.id] = a.word_count
        return self._articles

    def get_articlename(self):
        return self._articlename

    def get_noshow(self):
        return self._noshow

    def get_wordcount(self):
        return self._wordcount

    def set_noshow(self, show, no_show):
        for a in no_show:
            self._noshow[a] = True
        for a in show:
            self._noshow[a] = False
        for article in self._articles:
            article.noshow = self._noshow[article.article]
            db.session.add(article)
        db.session.commit()

    def diff_noshow(self):
        show = [key for key, value in self._noshow.items() if not value]
        no_show = [key for key, value in self._noshow.items() if value]
        return (no_show, show)


class Article_Sentence(object):

    def __init__(self):
        self._article = None
        self._sentence_id = 0
        self._sentence = []
        self._translation = []
        self._sentence_count = 0
        self._favorite_sentence_id = 0
        self._favorite_sentence = []
        self._favorite_translation = []
        self._favorite_sentence_count = 0

    def load(self,article):
        self._article = article
        mysentence = db.session.query(MySentence.sentence).all()
        mysentences = set([w[0] for w in mysentence])
        article_sentence = db.session.query(Sentence.id, Sentence.sentence, Sentence.translation).join(Article).filter(
            Article.article == article,
            Sentence.sentence.notin_(mysentences)
        ).order_by(Sentence.id).all()

        sentences_id = [w[0] for w in article_sentence]
        sentences = [w[1] for w in article_sentence]
        translations = [w[2] for w in article_sentence]

        self._sentence_id = sentences_id
        self._sentence = sentences
        self._translation = translations
        self._sentence_count = len(sentences)

        favorite_sentence = db.session.query(distinct(Sentence.id), Sentence.sentence, Sentence.translation).join(Article).join(SentenceReview).filter(
            Article.article == self._article,
            SentenceReview.known == True
        ).order_by(Sentence.id).all()

        self._favorite_sentence_id = [w[0] for w in favorite_sentence]
        self._favorite_sentence = [w[1] for w in favorite_sentence]
        self._favorite_translation = [w[2] for w in favorite_sentence]
        self._favorite_sentence_count = len(self._favorite_sentence)

        # print(self._favorite_sentence_id)
        # print(self._favorite_sentence)
        # print(self._favorite_translation)
        # print(self._favorite_sentence_count)

    def get_sentence_id(self):
        return self._sentence_id

    def get_sentence(self):
        return self._sentence

    def get_translation(self):
        return self._translation

    def get_sentence_count(self):
        return self._sentence_count

    def get_favorite_sentence_id(self):
        return self._favorite_sentence_id

    def get_favorite_sentence(self):
        return self._favorite_sentence

    def get_favorite_translation(self):
        return self._favorite_translation

    def get_favorite_sentence_count(self):
        return self._favorite_sentence_count


class Article_Word():

    def __init__(self):
        self._article = ''
        self._new_word = []
        self._favorite_word = []
        self._new_word_count = 0
        self._favorite_word_count = 0

    def load(self, article):
        self._article = article
        self._show_artile_words()

    def get_new_word(self):
        return self._new_word

    def get_new_word_count(self):
        return self._new_word_count

    def get_favorite_word(self):
        return self._favorite_word

    def get_favorite_word_count(self):
        return self._favorite_word_count

    def _show_artile_words(self):
        myword = db.session.query(MyWord.word).all()
        mywords = set([w[0] for w in myword])
        lemma = db.session.query(Lemma.lemma).filter(Lemma.word in mywords).all()
        lemmas = set(w[0] for w in lemma)

        nword = db.session.query(Word.word).join(ArticleWord).join(Article).filter(
            Article.article == self._article,
            Word.word.notin_(mywords or lemmas)
        ).order_by(Word.id).all()
        self._new_word = [w[0] for w in nword]
        self._new_word_count = len(self._new_word)

        favorite_word = db.session.query(distinct(Word.word)).join(ArticleWord).join(Article).join(WordReview).filter(
            Article.article == self._article,
            WordReview.known == True
        ).order_by(Word.word).all()

        self._favorite_word = [w[0] for w in favorite_word]
        self._favorite_word_count = len(self._favorite_word)



class LemmaDB (object):

    def __init__ (self):
        self._stems = {}
        self._words = {}
        self._frqs = {}

    # 读取数据
    def load (self, filename, encoding = None):
        content = open(filename, 'rb').read()
        if content[:3] == b'\xef\xbb\xbf':
            content = content[3:].decode('utf-8', 'ignore')
        elif encoding is not None:
            text = content.decode(encoding, 'ignore')
        else:
            text = None
            match = ['utf-8', sys.getdefaultencoding(), 'ascii']
            for encoding in match + ['gbk', 'latin1']:
                try:
                    text = content.decode(encoding)
                    break
                except:
                    pass
            if text is None:
                text = content.decode('utf-8', 'ignore')
        number = 0
        for line in text.split('\n'):
            number += 1
            line = line.strip('\r\n ')
            if (not line) or (line[:1] == ';'):
                continue
            pos = line.find('->')
            if not pos:
                continue
            stem = line[:pos].strip()
            p1 = stem.find('/')
            frq = 0
            if p1 >= 0:
                frq = int(stem[p1 + 1:].strip())
                stem = stem[:p1].strip()
            if not stem:
                continue
            if frq > 0:
                self._frqs[stem] = frq
            for word in line[pos + 2:].strip().split(','):
                p1 = word.find('/')
                if p1 >= 0:
                    word = word[:p1].strip()
                if not word:
                    continue
                self.add(stem, word.strip())
        return True

    # 保存数据文件
    def save (self, filename, encoding = 'utf-8'):
        stems = list(self._stems.keys())
        stems.sort(key = lambda x: x.lower())
        import codecs
        fp = codecs.open(filename, 'w', encoding)
        output = []
        for stem in stems:
            words = self.get(stem)
            if not words:
                continue
            frq = self._frqs.get(stem, 0)
            if frq > 0:
                stem = '%s/%d'%(stem, frq)
            output.append((-frq, u'%s -> %s'%(stem, ','.join(words))))
        output.sort()
        for _, text in output:
            fp.write(text + '\n')
        fp.close()
        return True

    # 添加一个词根的一个衍生词
    def add (self, stem, word):
        if stem not in self._stems:
            self._stems[stem] = {}
        if word not in self._stems[stem]:
            self._stems[stem][word] = len(self._stems[stem])
        if word not in self._words:
            self._words[word] = {}
        if stem not in self._words[word]:
            self._words[word][stem] = len(self._words[word])
        return True

    # 删除一个词根的一个衍生词
    def remove (self, stem, word):
        count = 0
        if stem in self._stems:
            if word in self._stems[stem]:
                del self._stems[stem][word]
                count += 1
            if not self._stems[stem]:
                del self._stems[stem]
        if word in self._words:
            if stem in self._words[word]:
                del self._words[word][stem]
                count += 1
            if not self._words[word]:
                del self._words[word]
        return (count > 0) and True or False

    # 清空数据库
    def reset (self):
        self._stems = {}
        self._words = {}
        return True

    def get_stems(self):
        stems = list(self._stems.keys())
        stems.sort(key = lambda x: x.lower())
        output = []
        for stem in stems:
            words = self.get(stem)
            if not words:
                continue
            frq = self._frqs.get(stem, 0)
            output.append((frq, stem, ','.join(words)))
        output.sort(reverse=True)
        return output

    # 根据词根找衍生，或者根据衍生反向找词根
    def get (self, word, reverse = False):
        if not reverse:
            if word not in self._stems:
                if word in self._words:
                    return [word]
                return None
            words = [ (v, k) for (k, v) in self._stems[word].items() ]
        else:
            if word not in self._words:
                if word in self._stems:
                    return [word]
                return None
            words = [ (v, k) for (k, v) in self._words[word].items() ]
        words.sort()
        return [ k for (v, k) in words ]

    # 知道一个单词求它的词根
    def word_stem (self, word):
        return self.get(word, reverse = True)

    # 总共多少条词根数据
    def stem_size (self):
        return len(self._stems)

    # 总共多少条衍生数据
    def word_size (self):
        return len(self._words)

    def dump (self, what = 'ALL'):
        words = {}
        what = what.lower()
        if what in ('all', 'stem'):
            for word in self._stems:
                words[word] = 1
        if what in ('all', 'word'):
            for word in self._words:
                words[word] = 1
        return words

    def __len__ (self):
        return len(self._stems)

    def __getitem__ (self, stem):
        return self.get(stem)

    def __contains__ (self, stem):
        return (stem in self._stems)

    def __iter__ (self):
        return self._stems.__iter__()


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, value, tb):
        self.duration = time.time() - self.start


def get_token(text):
    tokens = re.findall('[a-z]+', text.lower())
    tokens = list(dict.fromkeys(tokens))
    return tokens


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


def words_upper(sentence):
    new_words = set(article_word.get_new_word())
    for w in new_words:
        sentence = sentence.replace(w, w.upper())
    return sentence


article_word = Article_Word()
aritcle_sentence = Article_Sentence()
articles = Article_s()
article_file = Article_File()
my_word = My_Word()
