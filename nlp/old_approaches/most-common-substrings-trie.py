#!/usr/bin/env python3

import sys
import re
import json

TRIM_REGEX = re.compile(r'''[\s\.?!,;:\-\(\)\[\]\{\}'"。？！、；：・（）「」｛｝]''')

class WordCountTrie:
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

    COUNT_KEY = True

    def __init__(self):
        self._tree = {}

    def add(self, string):
        if len(string) == 0: return
        pivot = self._tree
        for char in string:
            if char not in pivot:
                pivot[char] = {}
            pivot = pivot[char]
        if WordCountTrie.COUNT_KEY not in pivot:
            pivot[WordCountTrie.COUNT_KEY] = 0
        pivot[WordCountTrie.COUNT_KEY] += 1

    def __iter__(self):
        stack = [iter(self._tree.items())]
        word = []
        while True:
            pivot = stack[-1]
            try:
                key, next_pivot_or_count = next(pivot)
                if key == WordCountTrie.COUNT_KEY:
                    yield ''.join(word), next_pivot_or_count
                    continue
                stack.append(iter(next_pivot_or_count.items()))
                word.append(key)
            except StopIteration:
                if len(stack) == 1:
                    break
                stack.pop()
                word.pop()


# tree = WordCountTrie()
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
    trie = WordCountTrie()
    for line in sys.stdin:
        count_substrings_trie(line, trie)

    results = filter_results(trie)
    del trie
    results = sort_results(results)

    for substring, amount in results:
        print(json.dumps([substring, amount], ensure_ascii=False))

if __name__ == '__main__':
    main()
