import re
from collections import Counter
import PyPDF2 as pdf
import os
import docx
from werkzeug import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def remove_empty_lines(file):
    if not os.path.isfile(file):
        print("{} does not exist ".format(file))
        return

    with open(file) as filehandle:
        lines = filehandle.readlines()

    lines = filter(lambda x: x.strip(), lines)
    lines = [x.lstrip() for x in lines]
    lines = [x for x in lines if not x.startswith('CHAPTER')]

    with open(file, 'w') as filehandle:
        filehandle.writelines(lines)

def get_english_chinese(file):
    if not os.path.isfile(file):
        print("{} does not exist ".format(file))
        return
    with open(file, 'r') as f:
        lines = f.read()
    lines = lines.split('\n')
    pttn = re.compile(r'(.*)[\s.!?]([\u4e00-\u9fa5].*)')
    line = [re.search(pttn,x).groups() for x in lines]
    return line


def split_sentence(string):
    pttn = f'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    sentences = re.split(pttn, string)
    ss = '\n'.join(sentences)
    with open('temp.txt','w') as f:
        f.write(ss)
    return ss


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_text(filename):
    if filename =='' or not allowed_file(filename):
        return ''
    fullText = []
    if filename[-4:] == '.txt':
        with open(filename,'r') as f:
            fullText = f.readlines()
        return '\n'.join(fullText)

    if filename[-4:] == '.pdf':
        with open(filename,'rb') as f:
            pdfReader = pdf.PdfFileReader(f)
            print(pdfReader.numPages)
            for pagenumber in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pagenumber)
                fullText.append(pageObj.extractText().lower())
        return '\n'.join(fullText)

    if filename[-4:] == 'docx':
        doc = docx.Document(filename)

        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    return ''

def read_text(filename):
    with open(filename, 'r') as f:
        text = f.read()
    return text

def get_sentence(file):
    with open(file, 'r') as f:
        text = f.read()
    pttn = re.compile(r"[a-zA-Z].*", re.I)
    sentences = re.findall(pttn, text)
    return sentences

def get_file_tokens(filename):
    tokens = get_tokens(read_text(get_file_by_name(filename)))
    return tokens

def get_tokens(text):
    tokens = re.findall('[a-z]+', text.lower())
    token = list(dict.fromkeys(tokens))
    return token

def create_token(file):
    csvfile = f'{file.split(".")[0]}.csv'
    text = read_text(file)
    token = get_tokens(text)
    count = Counter(token)

    token_new = []
    counter = 0
    with open(csvfile, 'w') as f:
        for c in (count.most_common()):
            counter += c[1]
            token_new.append(c)
            f.write(c[0]+', '+str(c[1])+'\n')
    return csvfile

def read_tokens(file):
    with open(file, 'r') as f:
        text = f.read()
    return get_tokens(text)


def get_file_by_type(filetype):
    sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        file = os.path.join(sourcedir, basename)
        basename = os.path.basename(file)
        extention = basename.split('.')[1]
        if extention == filetype:
            return file

def get_file_by_name(filename):
    if current_app.config.get('DEVELOPMENT'):
        sourcedir = current_app.config.get('UPLOAD_FOLDER')
    elif current_app.config.get('TEST'):
        sourcedir = current_app.config.get('TESTING_FOLDER')
    for basename in os.listdir(sourcedir):
        if basename.endswith('txt'):
            file = os.path.join(sourcedir, basename)
            basename = os.path.basename(file)
            if basename.startswith(filename):
                return file
    return None


def generate_sentence(key, statements ,file):
    text = read_text(file)
    with open(f'{file.split(".")[0]}_sentence.txt', 'a') as f:
        f.write(f'------------{key}-------------\n')
        for statement in statements:
            pttn = re.compile(r".*\b%s\b.*"%statement[0], re.I)
            # print(pttn)
            sentences = ((re.findall(pttn, text)))
            for sentence in sentences:
                f.write(sentence + '\n')

def generate_statement(key, file):
    text = read_text(file)
    pttn = re.compile(r"\b%s\b\W\w*"%key, re.IGNORECASE)
    statements = Counter(re.findall(pttn, text.lower()))
    with open(f'{file.split(".")[0]}_statement.txt', 'a') as f:
        f.write(f'------------{key}-------------\n')
        for s in statements.most_common():
            f.write(s[0] + '\n')
    return statements.most_common()

def generate(file):
    tokens = read_tokens(f'{file.split(".")[0]}_token.txt')
    f = open(f'{file.split(".")[0]}_sentence.txt', 'w')
    f.write('')
    f.close()
    f = open(f'{file.split(".")[0]}_statement.txt', 'w')
    f.write('')
    f.close()
    for token in tokens:
        statement = generate_statement(token, file)
        generate_sentence(token, statement, file)

def update_target_folder(sourcedir):
    enddirs = folder_sub(sourcedir)
    for dir in enddirs:
        path = os.path.join(dir, 'target')
        if not os.path.exists(path):
            os.makedirs(path)


def folder_sub(root,list=[]):
    #递归函数,返回所有叶节点source目录
    if folder_nosub(root):
        if os.path.isdir(root):
            list.append(root)
        return list
    else:
        for dir in os.listdir(root):
            path = os.path.join(root, dir)
            folder_sub(path, list)
    return list

def folder_nosub(root):
    if os.path.isdir(root):
        for o in os.listdir(root):
            path = os.path.join(root,o)
            if os.path.isdir(path) and o != 'target':
                return False
        return True
    else:
        return True

def create_txt(file):
    if os.path.isdir(file): return
    dirname = os.path.dirname(file)
    basename = os.path.basename(file)
    filename = basename.split('.')[0]
    wfile = os.path.join(dirname, secure_filename(filename)+'.txt')
    lines = get_text(file)
    with open(wfile, 'w') as f:
        pttn = f'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
        sentences = re.split(pttn, lines)
        ss = '\n'.join(sentences)
        f.write(ss)
    return wfile

def create_txt_from_target(sourcedir):
    dirs = folder_sub(sourcedir, [])
    for dir in dirs:
        for basename in os.listdir(dir):
            file = os.path.join(dir, basename)
            if os.path.isfile(file):
                dirname = os.path.dirname(file)
                filename = basename.split('.')[0]
                wfile = os.path.join(dirname,'target', secure_filename(filename)+'.txt')
                with open(wfile, 'a') as f:
                    lines = get_text(file)
                    pttn = f'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
                    sentences = re.split(pttn, lines)
                    f.write('\n'.join(sentences))

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

if __name__ == '__main__':
    pass
    # get_sentence('/Users/longliping/Developer/PyCharmProject/bdc/utility/upload/conv.txt', 'you')
    # str = 'chris wallace: (01:09:00)and what would you do about that?president donald j. trump: (01:09:01)theyõre not equippedé these people arenõt equipped to handle it, number one. number two, they cheat. they cheat. hey, they found ballots in a wastepaper basket three days ago, and they all had the name military ballots. there were military. they all had the name trump on them.chris wallace: (01:09:17)vice president biden-president donald j. trump: (01:09:17)you think thatõs good?chris wallace: (01:09:18)vice president biden, final question for you. will you urge your supporters to stay calm while the vote is counted? and will you pledge not to declare victory until the election is independently certified?vice president joe biden: (01:09:30)yes. and hereõs the deal. we count the ballots, as you pointed out. some of these ballots in some states canõt even be opened until election day. and if thereõs thousands of ballots, itõs going to take time to do it. and by the way, our militaryé theyõve been voting by ballots since the end of the civil war, in effect. and thatõs whatõs going to happen. why is it, for them, somehow not fraudulent. itõs the same process. itõs honest. no one has established at all that there is fraud related to mail-in ballots, that somehow itõs a fraudulent process.president donald j. trump: (01:10:07)itõs already been established. take a look at carolyn maloneyõs race-chris wallace: (01:10:10)i asked you. you had an opportunity to respond [crosstalk 01:10:13]. go ahead [crosstalk 01:10:14]. vice president biden, go ahead.vice president joe biden: (01:10:15)he has no idea what heõs talking about. hereõs the deal. the fact is, i will accept it, and he will too. you know why? because once the winner is declared after all the ballots are counted, all the votes are counted, thatõll be the end of it. thatõll be the end of it. and if itõs me, in fact, fine. if itõs not me, iõll support the outcome. and iõll be a president, not just for the democrats. iõll be a president for democrats and republicans. and this guy-president donald j. trump: (01:10:41)i want to see an honest ballot cut-chris wallace: (01:10:43)'
    # pttn = f'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    # split = re.split(pttn, str)
    # print(split)

