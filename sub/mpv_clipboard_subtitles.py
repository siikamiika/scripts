#!/usr/bin/env python3

import pyperclip
from tornado import websocket, web, ioloop
from pathlib import Path
import re
from mpv_python_ipc import MpvProcess
import sys
import time
from os.path import splitext
from queue import Queue


class Srt(object):

    def __init__(self, path):

        self.raw = Path(path).open(encoding='utf-8').read()
        if self.raw[0] == '\ufeff':
            self.raw = self.raw[1:]
        self.captions = []
        self._parse()
        self.last_idx = None


    def get_caption(self, t):

        if not self.captions:
            return

        i = self.last_idx or 0
        c = self.captions[i]

        backward = False
        while True:
            if c['start'] <= t and c['end'] >= t:
                if self.last_idx != i:
                    self.last_idx = i
                    return c['text']
                break
            elif c['end'] < t:
                if backward:
                    # we're between captions
                    break
                i += 1
            elif c['start'] > t:
                backward = True
                i -= 1

            if len(self.captions) <= i or i < 0:
                break

            c = self.captions[i]


    def _parse(self):

        status = None
        caption = None

        for l in self.raw.splitlines():
            if status == None:
                if re.match('^\d+$', l):
                    status = 'time'
            elif status == 'time':
                start, end = l.split('-->')
                if caption:
                    caption['text'] = '\n'.join(caption['text'])
                    self.captions.append(caption)
                caption = dict(start=self._parse_time(start), end=self._parse_time(end), text=[])
                status = 'text'
            elif status == 'text':
                if re.match('^\d+$', l):
                    status = 'time'
                else:
                    caption['text'].append(l)

        caption['text'] = '\n'.join(caption['text'])
        self.captions.append(caption)
        self.captions.sort(key=lambda c: c['start'])


    def _parse_time(self, t):
        h, m, s = t.strip().split(':')
        return int(h) * 60*60 + int(m) * 60 + float(s.replace(',', '.'))



clients = []


class WsHandler(websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            clients.append(self)

    def on_close(self):
        if self in clients:
            clients.remove(self)


def get_app():
    return web.Application([
        (r'/', WsHandler),
    ])



def main():

    video = sys.argv[1]
    srt = Srt(splitext(video)[0] + '.srt')
    mp = MpvProcess()

    mp.commandv('loadfile', video)

    def copysub(_, t):
        if not t:
            return
        d = mp.get_property_native('sub-delay') or 0
        text = srt.get_caption(t - d)
        if text:
            pyperclip.copy(text)
            for c in clients:
                c.write_message(text)

    mp.observe_property('time-pos', copysub)

    app = get_app()
    app.listen(9873)
    main_loop = ioloop.IOLoop.instance()
    main_loop.start()
    # # prevent closing the script before playback ends, but close everything at eof
    # end = Queue()
    # def quit():
    #     end.put(None)
    # mp.register_event('end-file', quit)
    # end.get(True)
    # mp.commandv('quit')
    

if __name__ == '__main__':
    main()
