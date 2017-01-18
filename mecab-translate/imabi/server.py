#!/usr/bin/env python3
from tornado import web, ioloop
from tornado.log import enable_pretty_logging; enable_pretty_logging()
import json
import re
import os
import time
from os.path import dirname, realpath, splitext, isfile
import sys
from bs4 import BeautifulSoup as BS

PROCESSED = 'imabi_processed/'

HIRAGANA_START = 0x3041
HIRAGANA_END = 0x3096
KATAKANA_START = 0x30A1
KATAKANA_END = 0x30FA
CJK_IDEO_START = 0x4e00
CJK_IDEO_END = 0x9faf

def is_kanji(char):
    return CJK_IDEO_START <= ord(char) <= CJK_IDEO_END

def is_kana(char):
    o = ord(char)
    if o > KATAKANA_END or o < HIRAGANA_START or HIRAGANA_END < o < KATAKANA_START:
        return False
    else:
        return True

def char_type(char):
    if is_kanji(char):
        return 'kanji'
    if is_kana(char):
        return 'kana'
    return None

class Search(object):

    def __init__(self):
        self.words = dict()
        self._parse_files()

    def search(self, text):

        terms = text.split()
        parsed_terms = []

        for term in terms:
            parsed_terms += self._split_text(term)

        if not len(parsed_terms):
            return []
        found = False
        for word in self.words:
            if parsed_terms[0] in word:
                if not found:
                    found = True
                    results = set(self.words[word])
                else:
                    results |= set(self.words[word])
        if not found:
            return []

        for term in parsed_terms[1:]:
            found = False
            for word in self.words:
                if term in word:
                    if not found:
                        found = True
                        temp_results = set(self.words[word])
                    else:
                        temp_results |= self.words[word]
            if not found:
                return list(results)
            results &= temp_results

        return list(results)

    def _parse_files(self):

        print('parsing html files...')
        start = time.time()

        for filename in os.listdir(PROCESSED):

            if not filename.endswith('.htm'):
                continue

            with open(PROCESSED + filename) as f:
                soup = BS(f.read(), 'html5lib')
            title = soup.find('h3', {'class': 'fw-title'})
            if not title:
                title = filename
            else:
                title = title.get_text().strip().replace('\n', ' ')
            words = soup.get_text().split()

            for w in words:
                parts = self._split_text(w)
                for p in parts:
                    if p not in self.words:
                        self.words[p] = set()
                    self.words[p].add((filename, title))

        print('    parsed in {:.2f} s'.format(time.time() - start))

    def _split_text(self, text):

        last_type = None
        output = []
        buffer = []
        for c in text:
            current_type = char_type(c)
            if last_type != current_type:
                if len(buffer):
                    output.append(''.join(buffer))
                    buffer = []
            buffer.append(c)
            last_type = current_type
        output.append(''.join(buffer).lower())
        return output

class SearchHandler(web.RequestHandler):

    def get(self):
        self.set_header('Cache-Control', 'max-age=3600')
        self.set_header('Content-Type', 'application/json')
        query = self.get_query_argument('query').strip()
        self.write(json.dumps(search.search(query)))

class IndexHandler(web.RequestHandler):

    def get(self):
        self.set_header('Cache-Control', 'max-age=3600')
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        with open('index.html') as f:
            self.write(f.read())

class StaticFileHandler(web.StaticFileHandler):

    def get_content_type(self):
        types = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.svg': 'image/svg+xml',
            '.js': 'application/javascript',
            '.css': 'text/css',
        }
        return (types.get(os.path.splitext(self.absolute_path)[1]) or
            'application/octet-stream')

def get_app():

    return web.Application([
        (r'/', IndexHandler),
        (r'/search', SearchHandler),
        (r'/(.*)', StaticFileHandler, {'path': 'imabi_processed'}),
    ])

if __name__ == '__main__':
    search = Search()
    address, port = (sys.argv[1] if len(sys.argv) > 1 else ':8085').split(':')
    app = get_app()
    app.listen(int(port), address=address)
    main_loop = ioloop.IOLoop.instance()
    print('done!')
    print('server listening to {}:{}'.format(address, port))
    main_loop.start()
