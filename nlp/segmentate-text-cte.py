#!/usr/bin/env python3

import sys
import json
import statistics

from lib import WordCountTrieSqlite

PHRASE_LIMIT = 10

def segmentate(phrase, trie):
    segments = []
    remaining = phrase
    while remaining:
        segment_at = trie.phrase_segment(remaining[:PHRASE_LIMIT])
        segments.append(remaining[:segment_at])
        remaining = remaining[segment_at:]
    return segments

def main():
    db_filename = sys.argv[1]
    phrases = sys.argv[3:]

    trie = WordCountTrieSqlite(db_filename)
    if not trie.load():
        raise Exception('No database! Populate it first')
    # TODO explore opportunities with the reverse trie

    if len(phrases) == 0:
        phrases = (phrase.strip() for phrase in sys.stdin)

    for phrase in phrases:
        print(segmentate(phrase, trie))

if __name__ == '__main__':
    main()
