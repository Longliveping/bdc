import re
from collections import Counter
import PyPDF2 as pdf
import os
import docx

def getText(filename):
    if filename[-4:] == 'docx':
        doc = docx.Document(filename)

        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)
    else:
        return ''

def read_text(filename):
    with open(filename, 'r') as f:
        text = f.read()
    return text

def tokens(text):
    token = re.findall('[a-z]+', text.lower())
    return token

def create_token(file):
    text = read_text(file)
    token = tokens(text)
    count = Counter(token)

    token_new = []
    counter = 0
    with open(f'{file.split(".")[0]}.csv', 'w') as f:
        for c in (count.most_common()):
            counter += c[1]
            token_new.append(c)
            f.write(c[0]+', '+str(c[1])+'\n')
    return token_new

def read_tokens(file):
    with open(file, 'r') as f:
        text = f.read()
    return tokens(text)

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

def update_target_folder():
    basedir = os.path.abspath(os.path.dirname(__file__))
    sourcedir = os.path.join(basedir, 'source')
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

def create_txt_from_docx():
    basedir = os.path.abspath(os.path.dirname(__file__))
    sourcedir = os.path.join(basedir, 'source')
    for dir in folder_sub(sourcedir):
        print(dir)
        for file in os.listdir(dir):
            if file[-4:] == 'docx':
                filename = file[:3]
                wfile = os.path.join(dir,'target', filename+'.txt')
                with open(wfile, 'a') as f:
                    lines = readDocx.getText(os.path.join(dir,file))
                    f.write(lines)

def create_token_target():
    basedir = os.path.abspath(os.path.dirname(__file__))
    sourcedir = os.path.join(basedir, 'source')
    for dir in folder_sub(sourcedir):
        target_dir = os.path.join(dir,'target')
        for file in os.listdir(target_dir):
            if file[-3:] == 'txt':
                wfile = os.path.join(target_dir, file)
                create_token(wfile)

if __name__ == '__main__':
    pass
    update_target_folder()
    create_txt_from_docx()
    create_token_target()




