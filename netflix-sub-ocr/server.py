#!/usr/bin/env python3

import time
import io
from base64 import b64decode
from subprocess import call

from tornado import websocket, web, ioloop
import pyocr
from PIL import Image

clients = []

def do_ocr(image_bytes):
    lang = "chi_sim"

    tool = pyocr.get_available_tools()[0]
    text = tool.image_to_string(Image.open(io.BytesIO(image_bytes)), lang=lang)
    text = "".join(text.split())

    for client in clients:
        client.write_message(text)


class WsHandler(websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        clients.append(self)

    def on_close(self):
        clients.remove(self)


class FakeImageHandler(web.RequestHandler):
    def get(self):
        image_data = self.get_arguments("image_data")
        image_data = image_data[0]
        _, image_b64 = image_data.split(",", 1)
        data = b64decode(image_b64)
        do_ocr(data)

def get_app():
    return web.Application([
        (r'/', WsHandler),
        (r'/fake_image', FakeImageHandler),
    ])


def main():
    address, port = '', 9873
    app = get_app()
    app.listen(port, address=address)
    main_loop = ioloop.IOLoop.instance()
    print('listening to {}:{}'.format(address, port))
    main_loop.start()

if __name__ == '__main__':
    main()
