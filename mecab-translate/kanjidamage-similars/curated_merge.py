#!/usr/bin/env python3
"""Merge KanjiDamage lookalikes into kanji.tgz_similars.ut8 but ask before committing"""

import json
from collections import OrderedDict

class SimilarsFile(object):

    def __init__(self, path, base=None):
        self.path = path
        if base:
            self.kanji = OrderedDict(base)
        else:
            self._parse()

    def _parse(self):
        self.kanji = OrderedDict()
        with open(self.path, 'r') as f:
            lines = f.read().splitlines()
        for l in lines:
            l = [k for k in l.split('/') if k.strip()]
            self.kanji[l[0]] = l[1:]

    def write(self):
        lines = ['{}/{}/'.format(c, '/'.join(self.kanji[c])) for c in self.kanji]
        with open(self.path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

    def get_similar(self, char):
        return self.kanji.get(char) or []

    def set_similar(self, char, similar):
        if char not in self.kanji:
            self.kanji[char] = []
        if similar not in self.kanji[char]:
            self.kanji[char].append(similar)

class LookalikeBlender(object):

    def __init__(self, original='kanji.tgz_similars.ut8', kanjidamage='kanjidamage_similars.json', output='kanji.tgz_similars.ut8'):
        self.original = SimilarsFile(original)
        self.kanjidamage = json.load(open(kanjidamage))
        self.output = SimilarsFile(output, self.original.kanji)

    def start(self):
        i = None
        for k in self.kanjidamage:
            if i == 'a':
                break
            for lookalike in self.kanjidamage[k]['similar']:
                if lookalike == k or lookalike in self.output.get_similar(k):
                    continue
                i = input('Do {} and {} look similar? (Y(es)/n(o)/a(bort)):'.format(k, lookalike))
                if i == 'a':
                    break
                elif i != 'n':
                    self.output.set_similar(k, lookalike)
                    self.output.set_similar(lookalike, k)
        self.output.write()

if __name__ == '__main__':
    blender = LookalikeBlender()
    blender.start()
