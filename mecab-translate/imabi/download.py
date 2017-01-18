#!/usr/bin/env python3
"""Make a local copy of imabi"""
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as BS

IMABI = 'http://www.imabi.net/'
ENC = 'latin-1'
UA = 'Mozilla/5.0'
DIR = 'imabi/'

def get_soup(url):
    """Download 'url' and parse it with BeautifulSoup"""
    req = Request(url, headers={'User-Agent': UA})
    return BS(urlopen(req).read().decode(ENC), 'html5lib')

def download():
    """Download imabi"""
    page = get_soup(IMABI)
    with open(DIR + 'index.html', 'w') as f:
        f.write(str(page))
    nav = page.find('ul', {'class': 'fw-nav-level-0'})
    sections = nav.find_all('a', {'class': 'section'})
    for section in sections:
        print(section['href'])
        filename = os.path.basename(section['href'])
        if not filename:
            continue
        section = get_soup(section['href'])
        with open(DIR + filename, 'w') as f:
            f.write(str(section))

def main():
    """Create directory and download"""
    try:
        os.makedirs(DIR)
    except FileExistsError:
        pass
    download()

if __name__ == '__main__':
    main()
