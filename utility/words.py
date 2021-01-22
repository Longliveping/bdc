import re, json
from collections import Counter
import PyPDF2 as pdf
import os, sys, time
import docx
from werkzeug import secure_filename
from flask import current_app
from app.models import db, Word, Lemma
from sqlalchemy import or_


def extract_srt(file):
    if not file or not allowed_file(file): return
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    sfile = os.path.join(dirname, secure_filename(filename)+'_sentence.json')
    wfile = os.path.join(dirname, secure_filename(filename)+'_word.json')
    tfile = os.path.join(dirname, secure_filename(filename)+'.tmp')
    if file[-4:] == '.srt':
        with open(file, 'r', encoding='utf8') as f:
            lines = f.read()
    if file[-4:] == '.tmp':
        with open(file, 'r', encoding='utf8') as f:
            lines = f.read()

    pttn = re.compile(r'\d{1,4}\n.*\n(.*)\n(.*)\n', re.M)
    lines = re.findall(pttn,lines)
    json_sentences = {}
    for count in range(len(lines)):
        key = re.sub(r'^[^\w]*','',lines[count][1])
        value = re.sub(r'[^\u4e00-\u9fa5]*','',lines[count][0])
        if re.match(r'^[A-Za-z]', key):
            json_sentences[key] = value

    word_list = [f'{key} : {value}' for key, value in json_sentences.items()]
    word_str = '\n'.join(word_list)
    with open(tfile,'w',encoding='utf8') as f:
        f.writelines(word_str)


    with open(sfile,'w',encoding='utf8') as f:
        json.dump(json_sentences,f,indent=4, ensure_ascii=False)

    word_str = '\n'.join(list(dict.fromkeys(json_sentences)))
    word_list = list(get_valid_token(word_str))
    json_words = {}
    for count in range(len(word_list)):
        json_words[word_list[count].strip()] = 1
    with open(wfile,'w',encoding='utf8') as f:
        json.dump(json_words,f,indent=4, ensure_ascii=False)

    return True


def extract_text(file):
    if file == '' or not allowed_file(file): return ''
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    sfile = os.path.join(dirname, secure_filename(filename)+'_sentence.json')
    wfile = os.path.join(dirname, secure_filename(filename)+'_word.json')
    tfile = os.path.join(dirname, secure_filename(filename)+'.tmp')
    fullText = []
    if file[-4:] == '.txt':
        with open(file, 'r') as f:
            fullText = f.readlines()
    elif file[-4:] == '.tmp':
        with open(file, 'r') as f:
            fullText = f.readlines()
    elif file[-4:] == '.pdf':
        with open(file, 'rb') as f:
            pdfReader = pdf.PdfFileReader(f)
            for pagenumber in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pagenumber)
                fullText.append(pageObj.extractText().lower())
    elif file[-4:] == 'docx':
        doc = docx.Document(file)
        for para in doc.paragraphs:
            fullText.append(para.text)

    fullText = '\n'.join(fullText)
    pttn = re.compile(r'([\w]+.*?[\.\?\!\n])', re.M)
    lines = re.findall(pttn,fullText)
    lines = [re.sub(r'\n','',x) for x in lines]
    fullText = '\n'.join(lines)
    with open(tfile, 'w') as f:
        f.writelines(fullText)

    if file[-4:] == '.tmp':
        json_words = {}
        for line in lines:
            json_words[line] = '1'
        with open(sfile,'w',encoding='utf8') as f:
            json.dump(json_words,f,indent=4, ensure_ascii=False)

        word_list = get_valid_token(fullText)
        json_words = {}
        for count in range(len(word_list)):
            json_words[word_list[count].strip()] = 1
        with open(wfile,'w',encoding='utf8') as f:
            json.dump(json_words,f,indent=4, ensure_ascii=False)

    return True


def read_word(file):
    file = _read_word_json_file(file)
    tokens = _read_token_json(file)
    return tokens


def read_word_by_filename(filename):
    file = read_file_by_name(filename)
    file = _read_word_json_file(file)
    tokens = _read_token_json(file)
    return tokens


def read_sentence(file):
    file = _read_sentence_json_file(file)
    j = _read_sentence_json(file)
    return j


def read_sentence_by_filename(filename):
    file = read_file_by_name(filename)
    file = _read_sentence_json_file(file)
    j = _read_sentence_json(file)
    return j


def read_word_by_file(file):
    tokens = get_token(read_text(file))
    return tokens

def read_valid_word_from_file(file):
    tokens = get_valid_token(read_text(file))
    return tokens

def get_valid_token(text):
    with Timer() as timer:
        tokens = re.findall('[a-z]+', text.lower())
        tokens = set(list(dict.fromkeys(tokens)))
        tokens = db.session.query(Word.word).join(Lemma).filter(or_(
            Lemma.lemma.in_(tokens),
            Word.word.in_(tokens)
        )).all()
        tokens = list(set([x[0] for x in tokens]))
    print('get valid token takes', timer.duration, 'seconds')
    return tokens


def get_token(text):
    tokens = re.findall('[a-z]+', text.lower())
    tokens = list(dict.fromkeys(tokens))
    return tokens


def create_sentence_srt_json(file):
    with open(file) as f:
        lines = f.readlines()
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    wfile = os.path.join(dirname, secure_filename(filename)+'_sentence.json')

    pttn = re.compile(r'(.*)[\s.!?]([\u4e00-\u9fa5].*)')
    lines = [re.search(pttn,x) for x in lines]
    lines = filter(lambda x: x, lines)
    lines = [x.groups() for x in lines]

    sentence_list = lines
    json_words = {}
    for count in range(len(sentence_list)):
        json_words[sentence_list[count][0].strip()] = sentence_list[count][1]

    with open(wfile,'w',encoding='utf8') as f:
        json.dump(json_words,f,indent=4, ensure_ascii=False)
    return json_words


def create_sentence_english_json(file):
    with open(file) as f:
        lines = f.read()
    pttn = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!|\n)'
    lines = re.split(pttn, lines)
    lines = filter(lambda x: len(x)>15 and len(x)<100, lines)
    lines = [re.sub(r'^[^\w]*','',x) for x in lines]
    json_words = {}
    for line in lines:
        json_words[line] = '1'
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    wfile = os.path.join(dirname, secure_filename(filename)+'_sentence.json')
    with open(wfile,'w') as f:
        json.dump(json_words,f,indent=4)
    return json_words


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'tmp','srt', 'pdf', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_text(file):
    with open(file, 'r') as f:
        text = f.read()
    return text


# looking for file
def read_file_by_type(filetype):
    sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        file = os.path.join(sourcedir, basename)
        basename = os.path.basename(file)
        extention = basename.split('.')[1]
        if extention == filetype:
            return file

def read_file_tmp(file):
    filename = os.path.basename(file).split('.')[0]
    dirname = os.path.dirname(file)
    tfile = os.path.join(dirname, filename+'.tmp')
    return tfile


def read_file_by_name(filename):
    sourcedir =[]
    if current_app.config.get('DEVELOPMENT'):
        sourcedir = current_app.config.get('UPLOAD_FOLDER')
    elif current_app.config.get('TESTING'):
        sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        if basename.endswith('tmp'):
            file = os.path.join(sourcedir, basename)
            basename = os.path.basename(file)
            if basename.startswith(filename):
                return file
    return None


def read_word_json_file(filename):
    sourcedir =[]
    if current_app.config.get('DEVELOPMENT'):
        sourcedir = current_app.config.get('UPLOAD_FOLDER')
    elif current_app.config.get('TESTING'):
        sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        if basename.endswith('word.json'):
            file = os.path.join(sourcedir, basename)
            basename = os.path.basename(file)
            if basename.startswith(filename):
                return file
    return None


def read_sentence_json_file(filename):
    sourcedir =[]
    if current_app.config.get('DEVELOPMENT'):
        sourcedir = current_app.config.get('UPLOAD_FOLDER')
    elif current_app.config.get('TESTING'):
        sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        if basename.endswith('sentence.json'):
            file = os.path.join(sourcedir, basename)
            basename = os.path.basename(file)
            if basename.startswith(filename):
                return file
    return None


def _create_sentence(file):
    if file == '' or not allowed_file(file): return ''
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    tfile = os.path.join(dirname, secure_filename(filename)+'.tmp')
    with open(file, 'r') as f:
        fullText = f.read()
    pttn = re.compile(r'([\w]+.*?)(?=[\.\?\!\n])', re.M)
    lines = re.findall(pttn,fullText)
    lines = [re.sub(r'\n','',x) for x in lines if len(x)>15]
    lines = '\n'.join(lines)
    with open(tfile, 'w+') as f:
        f.writelines(lines)
    return tfile


def _create_word_json(file):
    with open(file, 'r') as f:
        text = f.read()
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    wfile = os.path.join(dirname, secure_filename(filename)+'_word.json')
    word_list = get_token(text)
    json_words = {}
    for count in range(len(word_list)):
        json_words[word_list[count].strip()] = 1

    with open(wfile,'w',encoding='utf8') as f:
        json.dump(json_words,f,indent=4, ensure_ascii=False)
    return json_words


def _read_token_json(file):
    print('read token from json', file)
    with open(file, 'r') as f:
        j = json.load(f)
    tokens = j.keys()
    return tokens


def _read_sentence_json(file):
    with open(file, 'r') as f:
        j = json.load(f)
    return j


def _read_word_json_file(file):
    filename = os.path.basename(file).split('.')[0]
    dirname = os.path.dirname(file)
    wfile = os.path.join(dirname, filename+'_word.json')
    if os.path.isfile(wfile):
        return wfile
    return None


def _read_sentence_json_file(file):
    filename = os.path.basename(file).split('.')[0]
    dirname = os.path.dirname(file)
    sfile = os.path.join(dirname, filename+'_sentence.json')
    if os.path.isfile(sfile):
        return sfile
    return None


def update_target_folder(sourcedir):
    enddirs = folder_sub(sourcedir)
    for dir in enddirs:
        path = os.path.join(dir, 'target')
        if not os.path.exists(path):
            os.makedirs(path)


def folder_sub(root, l=[]):
    #递归函数,返回所有叶节点source目录
    if folder_nosub(root):
        if os.path.isdir(root):
            l.append(root)
        return l
    else:
        for dir in os.listdir(root):
            path = os.path.join(root, dir)
            folder_sub(path, l)
    return l


def folder_nosub(root):
    if os.path.isdir(root):
        for o in os.listdir(root):
            path = os.path.join(root,o)
            if os.path.isdir(path) and o != 'target':
                return False
        return True
    else:
        return True


def create_txt_from_target(sourcedir):
    dirs = folder_sub(sourcedir, [])
    for dir in dirs:
        for basename in os.listdir(dir):
            file = os.path.join(dir, basename)
            if os.path.isfile(file):
                dirname = os.path.dirname(file)
                filename = basename.split('.')[0]
                wfile = os.path.join(dirname,'target', secure_filename(filename)+'.txt')
                extract_text(wfile)
                # with open(wfile, 'a') as f:
                #     lines = extract_text(file)
                #     pttn = f'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
                #     sentences = re.split(pttn, lines)
                #     f.write('\n'.join(sentences))


def create_token(file):
    csvfile = f'{file.split(".")[0]}.csv'
    text = read_text(file)
    token = get_token(text)
    count = Counter(token)

    token_new = []
    counter = 0
    with open(csvfile, 'w') as f:
        for c in (count.most_common()):
            counter += c[1]
            token_new.append(c)
            f.write(c[0]+', '+str(c[1])+'\n')
    return csvfile


def create_token_target(sourcedir):
    for dir in folder_sub(sourcedir):
        target_dir = os.path.join(dir,'target')
        for file in os.listdir(target_dir):
            if file[-3:] == 'txt':
                wfile = os.path.join(target_dir, file)
                create_token(wfile)


def update_target(sourcedir):
    update_target_folder(sourcedir)
    create_txt_from_target(sourcedir)
    create_token_target(sourcedir)


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


if __name__ == '__main__':
    pass

