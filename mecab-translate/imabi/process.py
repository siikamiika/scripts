#!/usr/bin/env python3
"""Process the downloaded imabi copy suitable for offline use"""
import os
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup as BS
from bs4 import Comment

DL_DIR = 'imabi/'
OUTPUT_DIR = 'imabi_processed/'
UA = 'Mozilla/5.0'

BLACKLIST = {
    'element': [
        'script',
        'noscript',
        'style',
        'link',
        'iframe',
    ],
    'class': [
        'tealditDotComNewBarNotice',
        'Apple-tab-span',
    ],
    'id': [
        'contactme_tab',
        'fw-sidebar',
        'fw-head',
        'fw-mainnavwrap',
        'fw-footer',
    ],
    'attr': [
        'style',
        'size',
    ]
}

def download(url):
    """Download 'url'"""
    print(url)
    try:
        req = Request(url, headers={'User-Agent': UA})
        return urlopen(req).read()
    except:
        print('Failed to download')
        return b''

def get_soup(filename):
    """Parse a file with BeautifulSoup"""
    with open(filename, 'r') as f:
        data = f.read()
    return BS(data, 'html5lib')

def process():
    """Process the downloaded pages"""
    for filename in sorted(os.listdir(DL_DIR)):
        print(filename)
        page = get_soup(DL_DIR + filename)

        for element in page.find_all():
            for attr in BLACKLIST['attr']:
                try:
                    del element.attrs[attr]
                except:
                    pass

        for anchor in page.find_all('a'):
            try:
                anchor['href'] = os.path.basename(anchor['href'])
            except KeyError:
                pass

        for img in page.find_all('img'):
            try:
                url = img['src']
            except:
                continue
            netloc = urlparse(url).netloc
            if netloc in ['images.freewebs.com', 'www.paypal.com']:
                img.extract()
                continue
            img_filename = os.path.basename(url)
            img['src'] = img_filename
            if os.path.isfile(OUTPUT_DIR + img_filename):
                print('WARNING: skipping ' + img_filename)
                continue
            with open(OUTPUT_DIR + img_filename, 'wb') as f:
                f.write(download(url))

        for element in page.find_all(text=lambda text: isinstance(text, Comment)):
            element.extract()

        for element_name in BLACKLIST['element']:
            for element in page.find_all(element_name):
                element.extract()

        for bad_class in BLACKLIST['class']:
            for element in page.find_all(None, {'class': bad_class}):
                element.extract()

        for bad_id in BLACKLIST['id']:
            for element in page.find_all(None, {'id': bad_id}):
                element.extract()

        concise = page.new_tag('link', rel='stylesheet', href='concise.min.css', type='text/css')
        page.head.insert(0, concise)

        page.body['style'] = 'margin: 20px;'

        with open(OUTPUT_DIR + filename, 'w') as f:
            f.write(page.prettify())

def main():
    """Create output directory and process downloaded pages"""
    try:
        os.makedirs(OUTPUT_DIR)
    except FileExistsError:
        pass
    with open(OUTPUT_DIR + 'concise.min.css', 'wb') as f:
        f.write(download('https://cdn.concisecss.com/concise.min.css'))
    process()

if __name__ == '__main__':
    main()
