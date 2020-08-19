#!/usr/bin/env python3

import sys
import json

from lib import WordCountTrieSqlite

def hl(text):
    return '\033[0;31m' + text + '\33[0m'

def phrase_probability(phrase, trie, trie_reverse):
    phrase_tail = trie.find(phrase)
    if phrase_tail is None: return
    phrase_count = phrase_tail.count()

    phrase_head = trie_reverse.find(phrase[::-1])
    if phrase_head is None: return
    phrase_count2 = phrase_head.count()

    assert phrase_count == phrase_count2

    phrase_starts_count = 0
    for suffix, word_count in phrase_tail.deduped_suffixes():
        print(phrase + hl(suffix), word_count)
        phrase_starts_count += word_count

    phrase_ends_count = 0
    for prefix, word_count in phrase_head.deduped_suffixes():
        print(hl(prefix[::-1]) + phrase, word_count)
        phrase_ends_count += word_count

    return phrase_ends_count, phrase_count, phrase_starts_count

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
        print(phrase_probability(phrase, trie, trie_reverse))

if __name__ == '__main__':
    main()
