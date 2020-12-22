import urllib.request
from lxml import etree
import re
import time
from functools import reduce
import json



#获得页面数据
def get_page(myword):
    basurl='http://cn.bing.com/dict/search?q='
    searchurl=basurl+myword
    response =  urllib.request.urlopen(searchurl)
    html = response.read()
    return html

#获得单词释义
def get_chitiao(html_selector):
    chitiao=[]
    hanyi_xpath='/html/body/div[1]/div/div/div[1]/div[1]/ul/li'
    get_hanyi=html_selector.xpath(hanyi_xpath)
    for item in get_hanyi:
        it=item.xpath('span')
        chitiao.append(it[1].xpath('span')[0].text)
        # chitiao.append('%s\t%s'%(it[0].text,it[1].xpath('span')[0].text))
    return chitiao
    # if len(chitiao)>0:
    #     return reduce(lambda x, y:"%s\n%s"%(x,y),chitiao)
    # else:
    #     return ""

#获得单词音标和读音连接
def get_yingbiao(html_selector):
    yingbiao=[]
    yingbiao_xpath='/html/body/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div'
    bbb="(https\:.*?mp3)"
    reobj1=re.compile(bbb,re.I|re.M|re.S)
    get_yingbiao=html_selector.xpath(yingbiao_xpath)
    for item in get_yingbiao:
        it=item.xpath('div')
        if len(it)>0:
            ddd = ['a']
            print(ddd[0])
            try:
                ddd=reobj1.findall(it[1].xpath('a')[0].get('onmouseover',None))
                yingbiao.append({"phonetic":f'US {it[0].text[2:]}',"audio":ddd[0]})
                ddd=reobj1.findall(it[3].xpath('a')[0].get('onmouseover',None))
                yingbiao.append({"phonetic":f'UK {it[2].text[2:]}',"audio":ddd[0]})
            except:
                pass
    return yingbiao
    # if len(yingbiao)>0:
    #     return yingbiao
    #     # return reduce(lambda x, y:"%s\n%s"%(x,y),yingbiao)
    # else:
    #     return ""

#获得例句
def get_liju(html_selector):
    liju=[]
    get_liju_e=html_selector.xpath('//*[@class="val_ex"]')
    get_liju_cn=html_selector.xpath('//*[@class="bil_ex"]')
    get_len=len(get_liju_e)
    for i in range(get_len):
        liju.append("%s\t%s"%(get_liju_e[i].text,get_liju_cn[i].text))

    if len(liju)>0:
        return reduce(lambda x, y:"%s\n%s"%(x,y),liju)
    else:
        return ""

def get_word(word):
    aword = {
        "name": word,
        "chinese": [],
        "pronunciation": [{'phonetic': '', 'audio': ''}],
        "sentence": []
    }
    print(word)
    #获得页面
    pagehtml=get_page(word)
    selector = etree.HTML(pagehtml.decode('utf-8'))
    #单词释义
    chitiao=get_chitiao(selector)
    aword['chinese'] = chitiao
    #单词音标及读音
    yingbiao=get_yingbiao(selector)
    if len(yingbiao) > 0:
        aword['pronunciation'] = yingbiao
    #例句
    liju=get_liju(selector)

    return aword



if __name__ == '__main__':
    word = 'marsha'
    aword = get_word(word)
    print(aword)