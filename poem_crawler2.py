# from http://fanti.dugushici.com
# period: tang
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import re
import requests
import sys
import time


def get_poem(url, file=sys.stdout):
    r = None
    while r is None:
        try:
            r = requests.get(url)
        except ConnectionError:
            print('retrying...')
            time.sleep(2)
    r.encodeing = 'utf8'
    soup = BeautifulSoup(r.content, 'lxml')
    poem_section = soup.select_one('div.section2')
    poem = []
    for text in poem_section.find_all(text=True, recursive=False):
        cleaned_text = text.strip()
        if len(cleaned_text) == 0:
            continue
        ss = re.split('，|。|\.|\?|？', cleaned_text)
        for s in ss:
            if len(s.strip()) > 0:
                poem.append(s)
    print(len(poem), len(poem[0]), file=file)
    print('\n'.join(poem), file=file)
    print('Done poem')
    time.sleep(2)

base_url = 'http://fanti.dugushici.com'

with open('tang_poems_2.txt', 'a') as f:
    for page in range(262, 4717):
        query = '/ancient_proses/query?page=%d&q[prose_period_id_eq]=6'
        url = base_url + query

        r = None
        while r is None:
            try:
                r = requests.get(url % page)
            except ConnectionError:
                print('retrying')
                time.sleep(2)

        r.encoding = 'utf8'
        soup = BeautifulSoup(r.content, 'lxml')
        table = soup.select_one('div.common-list > table')
        is_header_parsed = False
        for tr in table.select('tr'):
            if not is_header_parsed:
                is_header_parsed = True
                continue

            tds = tr.select('td')
            title = tds[0].text
            link = base_url + tds[0].a.get('href')
            author = tds[2].text
            print(title, file=f)
            print(author, file=f)
            get_poem(link, file=f)
        f.flush()
        print('Done page %d' % page)
        time.sleep(10)
