#!/usr/bin/env python3

import sys
import random

from lib import WordCountTrieSqlite

def generate_text(trie, first_chars):
    next_first_chars = set()
    segments = [first_chars]
    pivot = trie
    while True:
        pivot = trie.find(''.join(segments[-6:])) or trie
        char = pivot.generate_char()
        string = ''.join(segments)

        has_repeating_pattern = False
        i = 0
        while True:
            i += 1
            chunk_len = 3 * i
            if len(string) <= chunk_len:
                break
            if len(set(string[-chunk_len:])) <= i:
                has_repeating_pattern = True
                break

        if char is None or has_repeating_pattern or len(string) > 60:
            next_first_chars |= set(string)
            for i in range(1, 4):
                next_first_chars |= set(string[j:j+i] for j in range(0, len(string) - i + 1))
            yield string
            segments = random.sample(next_first_chars, 1)
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
