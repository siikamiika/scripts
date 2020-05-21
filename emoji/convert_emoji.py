#!/usr/bin/env python3

import json
import re
import unicodedata

# https://github.com/joypixels/emoji-assets
with open('./emoji.json', 'rb') as f:
    data = f.read()

emoji_data = json.loads(data)
emoji_list = [emoji_data[k] for k in emoji_data]

for emoji in emoji_list:
    chars = [chr(int(c, 16)) for c in emoji['code_points']['base'].split('-')]
    full_char = ''.join(chars)

    shortname = emoji['shortname'].strip(':')

    keyword_list = []
    keyword_list += [shortname]
    keyword_list += re.split('[-_]', shortname)
    keyword_list += [kw for kw in emoji['keywords'] if not kw.startswith('uc')]

    keywords = set()
    for kw in keyword_list:
        kw = kw.lower()
        kw = kw.replace(' ', '_')
        kw = re.sub('[“”’.]', '', kw)
        kw = ''.join([unicodedata.normalize('NFD', c)[0] for c in kw])
        if kw == shortname:
            keywords.add(kw)
            continue
        if shortname.startswith(kw):
            continue
        keywords.add(f"{kw}_{shortname}")

    for kw in keywords:
        print(kw, full_char)
