#!/usr/bin/env python3

import sys
import re
import json

TRIM_REGEX = re.compile(r'''[\s\.?!,;:\-\(\)\[\]\{\}'"。？！、；：・（）「」｛｝]''')

def count_substrings(string, storage, count):
    string_len = len(string)
    for i in range(string_len):
        for j in range(i + 1, string_len + 1):
            substring = string[i:j]
            if TRIM_REGEX.match(substring[0]): continue
            if TRIM_REGEX.match(substring[-1]): continue
            if substring not in storage:
                storage[substring] = 0
            storage[substring] += 1
            count += 1
            print(count)
    return count


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
    count = 0
    substring_counts = {}
    for line in sys.stdin:
        count = count_substrings(line, substring_counts, count)

    results = filter_results(substring_counts.items())
    results = sort_results(results)

    for substring, amount in results:
        print(json.dumps([substring, amount], ensure_ascii=False))

if __name__ == '__main__':
    main()
