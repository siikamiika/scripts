#!/usr/bin/env python3

from collections import OrderedDict
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import time
import json
from sys import argv

class KanjiDamageSimilarKanjiScraper(object):

    def __init__(self, domain='http://www.kanjidamage.com', scrape_delay=1):
        self.domain = domain
        self.kanji = self._scrape_kanji_urls()
        self.scrape_delay = scrape_delay

    def scrape(self, output):
        for c in self.kanji:
            self.kanji[c]['similar'] = self._scrape_similar_kanji(c)
            print(c, self.kanji[c]['similar'])
            time.sleep(self.scrape_delay)
        with open(output, 'w') as f:
            json.dump(self.kanji, f)

    def _scrape_kanji_urls(self):
        data = urlopen(self.domain + '/kanji').read().decode()
        data = BS(data, 'html5lib')
        data = data.find('div', {'class': 'row'}).div.table
        out = OrderedDict()
        for c in data.find_all('tr'):
            c = c.find_all('td')[2].a
            char = c.text.strip()
            if char:
                out[char] = dict(url=c['href'], similar=[])
        return out

    def _scrape_similar_kanji(self, char):
        data = urlopen(self.domain + self.kanji[char]['url']).read().decode()
        data = BS(data, 'html5lib')
        data = data.find('h2', text='Lookalikes')
        out = []
        if not data:
            return out
        for c in data.next_sibling.next_sibling.find_all('tr')[1:]:
            c = c.td.text.strip()
            if c:
                out.append(c)
        return out


if __name__ == '__main__':
    scraper = KanjiDamageSimilarKanjiScraper()
    scraper.scrape(argv[1])
