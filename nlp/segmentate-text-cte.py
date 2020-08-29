#!/usr/bin/env python3

import sys

from lib import WordCountTrieSqlite

# database max depth is 20 characters currently
PHRASE_LIMIT = 10

def segmentate(phrase, trie):
    segments = []
    remaining = phrase
    while remaining:
        segment_results = trie.phrase_segment(remaining[:PHRASE_LIMIT])
        segment_at, score = segment_results[0]
        segments.append(remaining[:segment_at])
        print([(remaining[:segment_at2], score2) for segment_at2, score2 in segment_results])
        remaining = remaining[segment_at:]
    assert ''.join(segments) == phrase
    return segments

def main():
    db_filename = sys.argv[1]
    phrases = sys.argv[2:]

    trie = WordCountTrieSqlite(db_filename)
    # TODO explore opportunities with the reverse trie

    if len(phrases) == 0:
        phrases = (phrase.strip() for phrase in sys.stdin)

    for phrase in phrases:
        print(segmentate(phrase, trie))
        print('-------------------------------------------------------------------')

if __name__ == '__main__':
    main()
