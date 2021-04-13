#!/usr/bin/env python3

import pyperclip
from tornado import websocket, web, ioloop
from pathlib import Path
import re
from python_mpv_jsonipc import MPV
import sys
import time
from os.path import splitext, isfile
from queue import Queue

try:
    from tornado.platform.asyncio import AnyThreadEventLoopPolicy
    import asyncio
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
except:
    pass


class Subtitles(object):

    def __init__(self, path):

        try:
            self.raw = Path(path).open(encoding='utf-8').read()
        except:
            self.raw = Path(path).open(encoding='gbk').read()
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



class Srt(Subtitles):

    def _parse(self):

        def parse_time(t):
            h, m, s = t.strip().split(':')
            return int(h) * 60*60 + int(m) * 60 + float(s.replace(',', '.'))

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
                caption = dict(start=parse_time(start), end=parse_time(end), text=[])
                status = 'text'
            elif status == 'text':
                if re.match('^\d+$', l):
                    status = 'time'
                else:
                    caption['text'].append(l)

        caption['text'] = '\n'.join(caption['text'])
        self.captions.append(caption)
        self.captions.sort(key=lambda c: c['start'])


class Vtt(Subtitles):

    def _parse(self):

        def parse_time(t):
            h, m, s = t.strip().split(':')
            return int(h) * 60*60 + int(m) * 60 + float(s.replace(',', '.'))

        status = None
        caption = None

        for l in self.raw.splitlines():
            if re.match(r'^[\d:\.]+ --> [\d:\.]+$', l):
                start, end = l.split('-->')
                if caption:
                    caption['text'] = '\n'.join(caption['text'])
                    self.captions.append(caption)
                caption = dict(start=parse_time(start), end=parse_time(end), text=[])
                status = 'text'
            elif status == 'text':
                if not l:
                    status = 'time'
                else:
                    caption['text'].append(l)

        caption['text'] = '\n'.join(caption['text'])
        self.captions.append(caption)
        self.captions.sort(key=lambda c: c['start'])


class Ass(Subtitles):

    def _parse(self):

        def parse_time(t):
            h, m, s = t.split(':')
            return int(h) * 60*60 + int(m) * 60 + float(s)

        section = None
        fmt = None

        for l in self.raw.splitlines():

            if l and l[0] == '[' and l[-1] == ']':
                section = l[1:-1]
                continue

            if section == 'Events':
                if l.startswith('Format:'):
                    fmt = list(map(lambda l: l.strip(), l[len('Format:'):].split(',')))
                    continue
                if l.startswith('Dialogue:'):
                    dialogue = dict(zip(fmt,
                        map(lambda l: l.strip(), l[len('Dialogue:'):].split(',', len(fmt) - 1))))
                    self.captions.append(dict(
                        start=parse_time(dialogue['Start']),
                        end=parse_time(dialogue['End']),
                        text=dialogue['Text']
                        ))
                    continue

            self.captions.sort(key=lambda c: c['start'])



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
    video_base = splitext(video)[0]

    if isfile(video_base + '.srt'):
        sub = Srt(video_base + '.srt')
    elif isfile(video_base + '.ass'):
        sub = Ass(video_base + '.ass')
    elif isfile(video_base + '.vtt'):
        sub = Vtt(video_base + '.vtt')
    else:
        print('no subtitles found')
        return

    mp = MPV(script='~/.mpv/scripts/manual/focusplay.lua')

    mp.command('loadfile', video)

    @mp.property_observer('time-pos')
    def copysub(_, t):
        if not t:
            return
        d = mp.command('get_property', 'sub-delay') or 0
        text = sub.get_caption(t - d)
        if text:
            #pyperclip.copy(text)
            for c in clients:
                c.write_message(text)

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
