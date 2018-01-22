#!/usr/bin/env python3

import os
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from reibun import find_example_sentences

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class ReibunServer(HTTPServer):

    def set_path(self, path):
        self.path = path


class ReibunRequestHandler(BaseHTTPRequestHandler):

    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):
        pass

    def respond_ok(self, data=b'', content_type='text/html; charset=utf-8', age=0):
        self.send_response(200)
        self.send_header('Cache-Control', 'public, max-age={}'.format(age))
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def respond_notfound(self, data='404'.encode()):
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if url.path == '/':
            with open('index.html', 'rb') as f:
                self.respond_ok(f.read())
        elif url.path == '/search':
            text = query.get('text')
            if text:
                text = text[0]

            get_all = query.get('all')
            if get_all:
                get_all = True if get_all[0] == 'yes' else False

            response = find_example_sentences(self.server.path, text, get_all)
            response = json.dumps(response, ensure_ascii=False).encode('utf-8')
            self.respond_ok(response, content_type='application/json; charset=utf-8')
        else:
            self.respond_notfound()


def main():
    server = ReibunServer(('127.0.0.1', 9883), ReibunRequestHandler)
    server.set_path(sys.argv[1])
    server.serve_forever()


if __name__ == '__main__':
    main()
