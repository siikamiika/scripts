#!/usr/bin/env python3

import sys
import json
import statistics

from lib import WordCountTrieSqlite

def segmentate_test(phrase, trie):
    segments = []
    remaining = phrase
    while remaining:
        pivot = trie
        results = []
        for char in remaining:
            suffixes = list(pivot.suffixes(1, 1))
            if len(suffixes) == 0: break
            score_mean = statistics.mean(s[1] for s in suffixes)
            pivot = pivot.find(char)
            if pivot is None: break
            results.append((char, pivot.count() / score_mean))
        # TODO filter false positives with reverse trie
        if len(results) == 0:
            best_match_index = 1
        else:
            print(results)
            best_match_index = max(enumerate(results), key=lambda r: r[1][1])[0]
        segments.append(remaining[:best_match_index + 1])
        remaining = remaining[best_match_index + 1:]
    return segments

def main():
    db_filename = sys.argv[1]
    db_filename_reverse = sys.argv[2]
    phrases = sys.argv[3:]

    trie = WordCountTrieSqlite(db_filename)
    if not trie.load():
        raise Exception('No database! Populate it first')
    trie_reverse = WordCountTrieSqlite(db_filename_reverse)
    if not trie_reverse.load():
        raise Exception('No database! Populate it first')

    if len(phrases) == 0:
        phrases = (phrase.strip() for phrase in sys.stdin)

    for phrase in phrases:
        print(segmentate_test(phrase, trie))

if __name__ == '__main__':
    main()
