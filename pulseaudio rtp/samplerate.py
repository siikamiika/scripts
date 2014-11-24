#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
from urllib.parse import urlparse, parse_qsl
from threading import Thread
import sys
import time
import re

index = """<!DOCTYPE html>
<style>
</style>
<div style="font-size: 200%;">
<form action=samplerate>
    Sample rate (in Hz): <input type="text" name=val>
</form>
<form action=samplerate>
    <input type="hidden" name=val value=44100>
    <input type="submit" value="44100 Hz" style="font-size: 200%;">
</form>
<form action=samplerate>
    <input type="hidden" name=val value=48000>
    <input type="submit" value="48000 Hz" style="font-size: 200%;">
</form>
</div>
"""

def buffer_watchdog():
    global player
    last_exception = None
    while True:
        try:
            pipe = player.stderr
            read_until = b'\r'
            sys.stderr.flush()

            buf = b''
            while True:
                char = pipe.read(1)
                if char == b'':
                    time.sleep(0.1)
                    break
                buf += char
                if char == read_until:
                    sys.stdout.write(buf.decode())
                    audio_buffer = re.search(b'aq=.*?([0-9]+)KB.*?sq=', buf)
                    if audio_buffer:
                        buffer_size = int(audio_buffer.group(1))
                        if buffer_size > 12:
                            print('\n\nbuffer over 12KB, restarting ffplay\n\n')
                            player.kill()
                            player = Popen(player.args, stderr=PIPE)
                    break
        except Exception as e:
            if not last_exception == str(e):
                last_exception = str(e)
                print(e)
            time.sleep(0.1)

Thread(target=buffer_watchdog).start()

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.send_header('Content-Length', 0)
        self.end_headers()

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
        qs_list = dict(parse_qsl(url.query))
        if url.path == '/':
            self.respond_ok(index.encode())
        elif url.path == '/samplerate':
            global player
            ar = int(qs_list.get('val'))
            try:
                player.kill()
            except: pass
            player = Popen(['ffplay', '-nodisp', '-ar', str(ar), 'rtp://@239.255.12.34:4712/'], stderr=PIPE)
            self.redirect('/')
        else:
            self.respond_notfound()

if __name__ == "__main__":
    srv = HTTPServer(('', 9877), Handler)
    srv.serve_forever()
