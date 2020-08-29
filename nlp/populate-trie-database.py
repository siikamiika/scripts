#!/usr/bin/env python3

import sys
import re
import pathlib
import subprocess
import json
import io

from lib import WordCountTrieSqlite

def count_substrings_trie(string, trie):
    string_len = len(string)
    for i in range(string_len):
        range_start = i + 1
        range_stop = min(i + 21, string_len + 1) # exclusive, add 1
        for j in range(range_start, range_stop):
            substring = string[i:j]
            trie.add(substring)

def main():
    sources_filename = sys.argv[1]
    trie = WordCountTrieSqlite(sources_filename + '.wordcount_trie.db')
    total_line_count = 0
    for raw_desc in open(sources_filename):
        desc = json.loads(raw_desc)
        source_base_path = pathlib.Path(desc['base_dir'])
        if desc['mode'] == 'pipe':
            for source_path in source_base_path.rglob(desc['glob']):
                source_path = str(source_path)
                if trie.has_source(source_path):
                    print('{} already added, skipping'.format(source_path))
                    continue
                print('\n' + source_path)
                trie.add_source(source_path)
                extractor = subprocess.Popen(desc['extractor'], stdin=open(source_path), stdout=subprocess.PIPE)
                for text in io.TextIOWrapper(extractor.stdout, encoding='utf-8'):
                    count_substrings_trie(text.strip(), trie)
                    total_line_count += 1
                    print('\r{}'.format(total_line_count), end='')
        else:
            raise Exception('unknown mode: ' + desc['mode'])

if __name__ == '__main__':
    main()
