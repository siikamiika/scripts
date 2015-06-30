from urllib.request import urlopen, urlretrieve
import re
from datetime import datetime
import time
import sys
import os
import html

def get_data(url):
    return urlopen(url).read().decode()

def get_x(source, tag, all_tags=False):
    def _tag(fn):
        return fn('<{tag}>(.*?)</{tag}>'.format(tag=tag), source, re.S)
    if all_tags:
        return _tag(re.findall)
    else:
        match = _tag(re.search)
        match = html.unescape(match.group(1)) if match else ''
        return re.sub(r'\s+', ' ', match.strip())

def sanitize_filename(fn):
    fn = fn.replace('..', '')
    fn = re.sub(r'[/\\\"\']', '', fn)
    return re.sub(r'[^a-zA-Z0-9\-\.\(\) ]', '_', fn)

def get_items(rss_str):
    return get_x(rss_str, 'item', True)

def get_title(item):
    return get_x(item, 'title')

def get_link(item):
    return get_x(item, 'link')

def get_timestamp(item):
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pub_date = get_x(item, 'pubDate')
    pub_date = pub_date.split()[1:]
    pub_date[1] = str(MONTHS.index(pub_date[1]) + 1).zfill(2)
    pub_date = '{}/{}/{} {} {}'.format(*pub_date)
    pub_date = datetime.strptime(pub_date, '%d/%m/%Y %H:%M:%S %z')
    return time.mktime(pub_date.timetuple())

def main():
    url, folder = sys.argv[1:3]
    try: os.makedirs(folder)
    except: pass
    data = get_data(url)
    items = sorted([dict(
            filename=os.path.join(folder,
                sanitize_filename(get_title(item)) + '.torrent'),
            torrent_url=get_link(item),
            timestamp=get_timestamp(item)
        ) for item in get_items(data)], key=lambda i: i['timestamp'])

    for item in reversed(items):
        if os.path.isfile(item['filename']):
            break
        urlretrieve(item['torrent_url'], item['filename'])
        os.utime(item['filename'], (item['timestamp'],) * 2)

if __name__ == '__main__':
    main()
