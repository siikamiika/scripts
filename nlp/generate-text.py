#!/usr/bin/env python3

import sys
import random

from lib import WordCountTrieSqlite

def generate_text(trie, first_chars):
    chars = set()
    segments = [first_chars]
    pivot = trie
    while True:
        pivot = trie.find(''.join(segments[-5:])) or trie
        char = pivot.generate_char()
        string = ''.join(segments)
        if char is None or (len(string) > 3 and len(set(string[-3:])) == 1) or len(string) > 50:
            chars |= set(string)
            yield string
            segments = random.sample(chars, 1)
            pivot = trie
            continue
        segments.append(char)

def main():
    db_filename = sys.argv[1]
    first_chars = sys.argv[2] if len(sys.argv) > 2 else None

    trie = WordCountTrieSqlite(db_filename)
    if not trie.load():
        raise Exception('No database! Populate it first')

    for text in generate_text(trie, first_chars):
        print(text)

if __name__ == '__main__':
    main()
