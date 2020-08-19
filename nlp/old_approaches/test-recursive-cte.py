#!/usr/bin/env python3

import sys
import json
import time

from lib import WordCountTrieSqlite

def test_recursive_cte(phrase, trie, trie_reverse):
    phrase_tail = trie.find(phrase)
    if phrase_tail is None: return

    start = time.time()
    for s in phrase_tail.suffixes():
        print(s)
    print(time.time() - start)
    start = time.time()
    print('---------------------------')
    for s in phrase_tail.suffixes_cte_test():
        print(s)
    print(time.time() - start)

    assert set(phrase_tail.suffixes()) == set(phrase_tail.suffixes_cte_test())

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
        test_recursive_cte(phrase, trie, trie_reverse)

if __name__ == '__main__':
    main()
