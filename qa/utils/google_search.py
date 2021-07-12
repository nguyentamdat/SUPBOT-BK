from googleapiclient.discovery import build
from numpy import random
import requests
from bs4 import BeautifulSoup
import timeout_decorator
from nltk import sent_tokenize
from multiprocessing import Pool
import re
import sys
import os

api_key = ['AIzaSyCGZrRCGKDhwsdCKCh41XXgI92ZbxlUGsA' if os.environ["API_KEY"] is None else os.environ["API_KEY"]]

Custom_Search_Engine_ID = "005336700654283051786:1mzldt1husk"


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


@timeout_decorator.timeout(3)
def ggsearch(para):
    try:
        i = para[0]
        service = para[1]
        query = para[2]
        if (i == 0):
            res = service.cse().list(q=query, cx=Custom_Search_Engine_ID, gl='vn',
                                     googlehost='vn', hl='vi').execute()
        else:
            res = service.cse().list(q=query, cx=Custom_Search_Engine_ID, num=5, start=i*5, gl='vn',
                                     googlehost='vn', hl='vi').execute()
        return res[u'items']
    except:
        return []


@timeout_decorator.timeout(7)
def getContent(url):
    try:
        html = requests.get(url, timeout=10)
        # print(html)
        tree = BeautifulSoup(html.text, 'lxml')
        for invisible_elem in tree.find_all(['script', 'style']):
            invisible_elem.extract()

        paragraphs = [p.get_text() for p in tree.find_all("p")]

        for para in tree.find_all('p'):
            para.extract()

        for href in tree.find_all(['a', 'strong']):
            href.unwrap()

        tree = BeautifulSoup(str(tree.html), 'lxml')

        text = tree.get_text(separator='\n\n')
        text = re.sub('\n +\n', '\n\n', text)

        paragraphs += text.split('\n\n')
        paragraphs = [re.sub(' +', ' ', p.strip()) for p in paragraphs]
        paragraphs = [p for p in paragraphs if len(p.split()) > 10]

        for i in range(0, len(paragraphs)):
            sents = []
            text_chunks = list(chunks(paragraphs[i], 100000))
            for chunk in text_chunks:
                sents += sent_tokenize(chunk)

            sents = [s for s in sents if len(s) > 2]
            sents = ' . '.join(sents)
            paragraphs[i] = sents
        return '\n\n'.join(paragraphs)
    except:
        print('Cannot read ' + url, str(sys.exc_info()[1]))
        return ''


class _GoogleSearch():
    _instance = None

    def __init__(self):
        print("create instance")
        self.pool = Pool(4)
        # import nltk
        # nltk.download('punkt')

    def search(self, question):
        print("searching")
        service = build("customsearch", "v1", developerKey=api_key[random.randint(
            0, len(api_key))], cache_discovery=False)
        pages_content = self.pool.map(
            ggsearch, [(i, service, question) for i in range(0, 2)])
        pages_content = [j for i in pages_content for j in i]

        document_urls = set([])
        for page in pages_content:
            if 'fileFormat' in page:
                continue
            document_urls.add(page[u'link'])
        document_urls = list(document_urls)

        gg_documents = self.pool.map(getContent, document_urls)
        gg_documents = [d for d in gg_documents if len(d) > 20]
        print("searched")
        # print(gg_documents)

        return document_urls, gg_documents


def GoogleSearch():
    if _GoogleSearch._instance is None:
        _GoogleSearch._instance = _GoogleSearch()
    return _GoogleSearch._instance
