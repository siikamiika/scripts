#!/usr/bin/env python3

import sys
import re
import json

TRIM_REGEX = re.compile(r'''[\s\.?!,;:\-\(\)\[\]\{\}'"。？！、；：・（）「」｛｝]''')

class WordCountTrieSqlite:
    # {
    #   "a": {
    #      "b": {
    #        True: 1
    #      },
    #      "c": {
    #        True: 2
    #      }
    #   },
    #   "x": {
    #     True: 3
    #   }
    # }

    def __init__(self):
        self._tree = [None, 0, []]

    def add(self, string):
        if len(string) == 0: return
        pivot = self._tree
        for char in string:
            for next_pivot in pivot[2]:
                if char == next_pivot[0]:
                    pivot = next_pivot
                    break
            else:
                next_pivot = [char, 0, []]
                pivot[2].append(next_pivot)
                pivot = next_pivot
        pivot[1] += 1

    def __iter__(self):
        stack = [iter(self._tree[2])]
        word = []
        while True:
            pivot = stack[-1]
            try:
                char, word_count, next_pivot = next(pivot)
                word.append(char)
                if word_count > 0:
                    yield ''.join(word), word_count
                stack.append(iter(next_pivot))
            except StopIteration:
                if len(stack) == 1:
                    break
                stack.pop()
                word.pop()


# tree = WordCountTrieSqlite()
# tree.add('asdf')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('asdg')
# tree.add('xd')
# tree.add('xdd')
# tree.add('')
# print(tree._tree)
# print(json.dumps(tree._tree))
# print(list(tree))

# exit(1)


def count_substrings_trie(string, trie):
    string_len = len(string)
    for i in range(string_len):
        for j in range(i + 1, string_len + 1):
            substring = string[i:j]
            if TRIM_REGEX.match(substring[0]): continue
            if TRIM_REGEX.match(substring[-1]): continue
            trie.add(substring)


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
    trie = WordCountTrieSqlite()
    for line in sys.stdin:
        count_substrings_trie(line, trie)

    results = filter_results(trie)
    del trie
    results = sort_results(results)

    for substring, amount in results:
        print(json.dumps([substring, amount], ensure_ascii=False))

if __name__ == '__main__':
    main()
