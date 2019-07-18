#!/usr/bin/env python3

import io
import functools
from base64 import b64decode
from subprocess import call

from tornado import websocket, web, ioloop
import pyocr
from PIL import Image, ImageOps

LANG = "chi_sim"

clients = []

@functools.lru_cache(maxsize=100)
def do_ocr(image_bytes):
    lines = []

    tool = pyocr.get_available_tools()[0]

    image = Image.open(io.BytesIO(image_bytes))

    canvas = Image.new("RGB", image.size, (0, 0, 0))
    canvas.paste(image, mask=image.split()[3])
    image = canvas
    image = ImageOps.invert(image)
    # image.save("img.png")

    x, y = image.size
    cur = 74
    while cur - y < 10:
        row = image.crop((0, cur - 74, x, cur))
        lines.append(tool.image_to_string(row, lang=LANG))
        cur += 74

    lines = ["".join(l.split()) for l in lines]

    return "\n".join(lines)



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
        text = do_ocr(data)
        for client in clients:
            client.write_message(text)

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
