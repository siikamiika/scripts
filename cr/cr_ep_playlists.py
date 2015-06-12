import sys
import os
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import html5lib
from bs4 import BeautifulSoup as BS
import re

def sanitize_filename(fn):
    fn = fn.replace('..', '')
    fn = re.sub(r'[/\\\"\']', '', fn)
    return re.sub(r'[^a-zA-Z0-9\-\.\(\) ]', '_', fn)

def get_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    return BS(data, 'html5lib')

def get_seasons(page):
    season_list = page.find('ul', {'class': 'list-of-seasons'})
    return season_list.find_all('li', {'class': 'season'})

def get_episodes(season):
    episodes = season.ul.find_all('li')
    return [e.a for e in episodes]

def main():
    anime_url = urlparse(sys.argv[1])
    anime_name = sanitize_filename(anime_url.path.split('/')[1])
    seasons = get_seasons(get_soup(anime_url.geturl()))
    for s in seasons:
        season_name = sanitize_filename(s.a.string.strip())
        try:
            os.makedirs('{}/{}'.format(anime_name, season_name))
        except Exception as e:
            print(e)
        episodes = get_episodes(s)
        for e in episodes:
            episode_url = e['href']
            if not episode_url.startswith('http'):
                if episode_url.startswith('/'):
                    episode_url = '{url.scheme}://{url.netloc}{ep}'.format(
                        url=anime_url, ep=episode_url)
                else:
                    episode_url = '{}/{}'.format(anime_url.geturl(), episode_url)
            episode_name = '{} - {}'.format(
                e.span.string.strip(),
                e.p.string.strip())
            episode_filename = sanitize_filename(episode_name)
            episode_filename = '{}/{}/{}.m3u'.format(
                anime_name, season_name, episode_filename)
            if not os.path.isfile(episode_filename):
                with open(episode_filename, 'w') as f:
                    f.write('#EXTM3U\n{}'.format(episode_url))

if __name__ == '__main__':
    main()
