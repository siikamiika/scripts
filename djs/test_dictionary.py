#!/usr/bin/env python3

import csv
import sys
from collections import OrderedDict

class Dictionary(object):

    def __init__(self):
        self.index = self._read_index()
        self.data = self._read_data()

    def lookup(self, word):
        output = []
        for index in self.index[word]:
            output.append(self.data[index])
        return output

    def _read_index(self):
        output = OrderedDict()
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                output[row[0]] = [int(i) for i in row[1].split('|')]
        return output

    def _read_data(self):
        output = dict()
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                output[int(row[0])] = row[2:]
        return output

def main():
    dictionary = Dictionary()
    while True:
        results = dictionary.lookup(input('query: '))
        for r in results:
            print('\n'.join(r))

if __name__ == '__main__':
    main()
