import sys
import html5lib
from bs4 import BeautifulSoup as BS
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qsl
import re
import os

UA_STRING = 'Mozilla/5.0'

def sanitize_filename(fn):
    fn = fn.replace('..', '')
    fn = re.sub(r'[/\\\"\']', '', fn)
    return re.sub(r'[^a-zA-Z0-9\-\.\(\) ]', '_', fn)

def get_soup(url):
    req = Request(url, headers={'User-Agent': UA_STRING})
    page = urlopen(req).read().decode()
    return BS(page, 'html5lib')

def get_playlist_entries(soup):
    vid_table = soup.find(id='pl-video-table')
    videos = vid_table.find_all('tr')
    videos = [v.find_all('a') for v in videos]
    videos = [next(a for a in v if a.text.strip()) for v in videos]
    return [
        (   # [0]: video url
            'https://www.youtube.com/watch?v={}'.format(
                dict(parse_qsl(urlparse(a['href']).query))['v']),
            re.sub(r'\s+', ' ', a.text.strip()) # [1]: video title
        )
        for a in videos]

def write_playlist(location, url, title, index=None):
    fn = index + '_' if index else ''
    fn += sanitize_filename(title) + '.m3u'
    fn = os.path.join(location, fn)
    if not os.path.isfile(fn):
        print(fn)
        with open(fn, 'w') as f:
            f.write('#EXTM3U\n{}'.format(url))

def parse_args(args):
    for arg in args:
        if arg.startswith('http'):
            url = arg
        else:
            location = arg
    return location, url

def main():
    location, url = parse_args(sys.argv[1:])
    try: os.makedirs(location)
    except: pass
    entries = get_playlist_entries(get_soup(sys.argv[1]))
    entry_len_len = len(str(len(entries) + 1))
    for i, e in enumerate(entries):
        idx = '{}'.format(i + 1).zfill(entry_len_len)
        write_playlist(location, *e, index=idx)

if __name__ == '__main__':
    main()
