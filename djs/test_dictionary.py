#!/usr/bin/env python3

import csv
import sys
import os
from collections import OrderedDict
from tornado import web, ioloop
from tornado.log import enable_pretty_logging; enable_pretty_logging()
import json


class Dictionary(object):

    def __init__(self):
        self.index = self._read_index()
        self.data = self._read_data()

    def lookup(self, word):
        output = []
        for index in self.index[word]:
            output.append(self.data[index])
        return output

    def _read_index(self):
        output = OrderedDict()
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                output[row[0]] = [int(i) for i in row[1].split('|')]
        return output

    def _read_data(self):
        output = dict()
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                output[int(row[0])] = row[2:]
        return output

class DictionaryHandler(web.RequestHandler):

    def get(self):
        self.set_header('Cache-Control', 'max-age=3600')
        self.set_header('Content-Type', 'application/json')
        query = self.get_query_argument('query').strip()
        response = dictionary.lookup(query)
        self.write(json.dumps(response))

class StaticFileHandler(web.StaticFileHandler):

    def get_content_type(self):
        types = {
            '.html': 'text/html',
            '.svg': 'image/svg+xml',
            '.js': 'application/javascript',
            '.css': 'text/css',
        }
        return (types.get(os.path.splitext(self.absolute_path)[1]) or
            'application/octet-stream')

def get_app():

    return web.Application([
        (r'/dictionary', DictionaryHandler),
        (r'/(.*)', StaticFileHandler,
            {'path': 'client', 'default_filename': 'index.html'}),
    ])

if __name__ == '__main__':
    dictionary = Dictionary()
    address, port = ':9879'.split(':')
    app = get_app()
    app.listen(int(port), address=address)
    main_loop = ioloop.IOLoop.instance()
    print('done!')
    print('server listening to {}:{}'.format(address, port))
    main_loop.start()
