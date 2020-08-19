#!/usr/bin/env python3

import sys
import re

from lib import WordCountTrieSqlite

TRIM_REGEX = re.compile(r'''[\s\.?!,;:\-\(\)\[\]\{\}'"。？！、；：・（）「」｛｝]''')

def count_substrings_trie(string, trie):
    string_len = len(string)
    for i in range(string_len):
        range_start = i + 1
        range_stop = min(i + 21, string_len + 1) # exclusive, add 1
        for j in range(range_start, range_stop):
            substring = string[i:j]
            if TRIM_REGEX.match(substring[0]): continue
            if TRIM_REGEX.match(substring[-1]): continue
            trie.add(substring)

def generate_trie(strings, output_filename):
    trie = WordCountTrieSqlite(output_filename)
    if not trie.load():
        for string in strings:
            count_substrings_trie(string.strip(), trie)
        trie.persist()

def main():
    input_filename = sys.argv[1]
    generate_trie(open(input_filename), input_filename + '.wordcount_trie.db')
    generate_trie((s[::-1] for s in open(input_filename)), input_filename + '.wordcount_trie_reverse.db')

if __name__ == '__main__':
    main()
