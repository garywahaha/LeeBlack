from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests


def get_tonals():
    url = 'https://zh.wikisource.org/zh-hant/%E5%B9%B3%E6%B0%B4%E9%9F%BB'
    r = requests.get(url)
    r.encoding = 'big5'
    soup = BeautifulSoup(r.content, 'lxml')
    opts = soup.find_all('h2')
    n = len(opts)
    for i, opt in enumerate(opts):
        h = opt.find('span', class_='mw-headline')
        if h is not None:
            nt = None
            if i < n-1:
                nt = opts[i+1]
            idx = opt.text.find('聲')
            title = opt.text[:idx]
            cur = opt.next_sibling
            rhyme = ''
            while cur is not None and cur != nt:
                if not isinstance(cur, NavigableString):
                    if cur.name == 'table':
                        break
                    if title + '聲' not in cur.text:
                        s = cur.text
                        if '】' in s:
                            s = s[s.find('】')+1:]
                        for x in s:
                            print(x, title, rhyme)
                    else:
                        rhyme = cur.text[-1]
                cur = cur.next_sibling

get_tonals()
