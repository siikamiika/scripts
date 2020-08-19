#!/usr/bin/env python3

import sys
import json

from lib import WordCountTrieSqlite

def filter_results(results):
    for substring, amount in results:
        if amount == 1:
            continue
        yield substring, amount


def sort_results(results):
    def sort(result):
        return result[1], len(result[0])
    return sorted(results, key=sort, reverse=True)


def main():
    db_filename = sys.argv[1]
    trie = WordCountTrieSqlite(db_filename)
    if not trie.load():
        raise Exception('No database! Populate it first')

    results = filter_results(trie)
    results = sort_results(results)

    for substring, amount in results:
        print(json.dumps([substring, amount], ensure_ascii=False))

if __name__ == '__main__':
    main()
