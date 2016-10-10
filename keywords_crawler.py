from bs4 import BeautifulSoup
import requests


def get_keyword_categories():
    url = 'http://cls.hs.yzu.edu.tw/MakePoem/qry_type.asp'
    r = requests.get(url)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.content, 'lxml')
    opts = soup.find_all('option')
    for opt in opts:
        result = {
            'id': opt.get('value'),
            'str': opt.text.replace(' ', ''),
        }
        yield result


def get_keyword_classes(category):
    url = 'http://cls.hs.yzu.edu.tw/MakePoem/qry_name.asp'
    data = {
        'TypeList': category['id'],
        'SELTYPE': u'查詢',
    }
    r = requests.post(url, data=data)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.content, 'lxml')
    opts = soup.find_all('option')
    for opt in opts:
        result = {
            'id': opt.get('value'),
            'str': opt.text.replace(' ', ''),
        }
        if result['id'] not in [' ']:
            yield result


def get_keywords(k_class):
    url = 'http://cls.hs.yzu.edu.tw/MakePoem/qry_body.asp'
    data = {
        'NameList': k_class['id'],
        'SELTYPE': u'查詢',
    }
    r = requests.post(url, data=data)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.content, 'lxml')
    keywords = soup.find_all('td')
    for keyword in keywords:
        yield keyword.text.replace(' ', '')


with open('keywords.txt', 'w') as f:
    categories = list(get_keyword_categories())
    print(len(categories), file=f)
    for category in categories:
        classes = list(get_keyword_classes(category))
        print(category['str'], file=f)
        print(len(classes), file=f)
        for k_class in classes:
            keywords = list(get_keywords(k_class))
            print(k_class['str'], file=f)
            print(len(keywords), file=f)
            print('\n'.join(keywords), file=f)

            print('Done class %s' % k_class['str'])

        print('Done category %s' % category['str'])
