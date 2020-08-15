#!/usr/bin/env python3

import os
import json
import hashlib
import fontforge
import subprocess

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

def trace_image(path):
    magick = subprocess.Popen(['convert', path, 'bmp:-'], stdout=subprocess.PIPE)
    magick.wait()
    potrace = subprocess.Popen(['potrace', '--backend', 'svg', '--alphamax', '0', '--opttolerance', '0'], stdin=magick.stdout, stdout=subprocess.PIPE)
    potrace.wait()
    output_path = path + '.svg'
    with open(output_path, 'wb') as f:
        f.write(potrace.stdout.read())
    return output_path

def main():
    font = fontforge.font()
    font.encoding = 'UnicodeBmp'

    with open(os.path.join(SCRIPT_PATH, 'mapped_emoji.json')) as f:
        emoji_to_url = json.loads(f.read())

    for emoji, url in emoji_to_url.items():
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
        image_path = os.path.join(SCRIPT_PATH, 'image_cache', 'emoji', url_hash)
        svg_path = trace_image(image_path)
        glyph = font.createMappedChar(int(emoji))
        glyph.importOutlines(svg_path)

    font.generate(os.path.expanduser('~/.local/share/fonts/LiveChat.ttf'))

if __name__ == '__main__':
    main()
