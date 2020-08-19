#!/usr/bin/env python3

import os
import sys
import re
import json
import sqlite3

TRIM_REGEX = re.compile(r'''[\s\.?!,;:\-\(\)\[\]\{\}'"。？！、；：・（）「」｛｝]''')

class WordCountTrieSqlite:
    def __init__(self, path):
        self._path = path
        self._conn = sqlite3.connect(':memory:')
        self._cursor = self._conn.cursor()
        self._ensure_table()

    def add(self, string):
        #  0   1          2     3
        # (id, parent_id, char, count)
        if len(string) == 0: return
        pivot = self._get_root()
        for char in string:
            pivot = self._get_child(pivot[0], char) or self._create_child(pivot[0], char)
        self._increment_wordcount(pivot[0])

    def load(self):
        if os.path.isfile(self._path):
            backup = sqlite3.connect(self._path)
            with backup:
                backup.backup(self._conn)
            backup.close()
            return True
        return False

    def persist(self):
        backup = sqlite3.connect(self._path)
        with backup:
            self._conn.backup(backup)
        backup.close()

    def _ensure_table(self):
        self._run_sql('''
            CREATE TABLE IF NOT EXISTS wordcount_trie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                char TEXT,
                count INTEGER DEFAULT 0
            )
        ''')
        self._run_sql('CREATE INDEX IF NOT EXISTS parent ON wordcount_trie (parent_id)')
        self._run_sql('CREATE UNIQUE INDEX IF NOT EXISTS char_parent ON wordcount_trie (char, parent_id)')
        if len(self._run_sql('SELECT * FROM wordcount_trie WHERE id = 1')) == 0:
            self._run_sql('INSERT INTO wordcount_trie DEFAULT VALUES') # (id=1, parent_id=None, char=None, count=0)

    def _run_sql(self, statement, params=None):
        if params is not None:
            self._cursor.execute(statement, params)
        else:
            self._cursor.execute(statement)
        self._conn.commit()
        return self._cursor.fetchall()

    def _get_root(self):
        return self._run_sql('SELECT * FROM wordcount_trie WHERE id = 1')[0]

    def _get_child(self, parent_id, char):
        results = self._run_sql('SELECT * FROM wordcount_trie WHERE parent_id = ? AND char = ?', [parent_id, char])
        if len(results) == 0: return None
        return results[0]

    def _get_children(self, parent_id):
        return self._run_sql('SELECT * FROM wordcount_trie WHERE parent_id = ?', [parent_id])

    def _create_child(self, parent_id, char):
        self._run_sql('INSERT INTO wordcount_trie (parent_id, char) VALUES (?, ?)', [parent_id, char])
        return (self._cursor.lastrowid, parent_id, char, 0)

    def _increment_wordcount(self, id):
        self._run_sql('UPDATE wordcount_trie SET count = count + 1 WHERE id = ?', [id])

    def __iter__(self):
        root = self._get_root()
        stack = [iter(self._get_children(root[0]))]
        word = []
        while True:
            pivot = stack[-1]
            try:
                id, _, char, word_count = next(pivot)
                word.append(char)
                if word_count > 0:
                    yield ''.join(word), word_count
                stack.append(iter(self._get_children(id)))
            except StopIteration:
                if len(stack) == 1:
                    break
                stack.pop()
                word.pop()


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
    input_filename = sys.argv[1]
    trie = WordCountTrieSqlite(input_filename + '.wordcount_trie.db')
    if not trie.load():
        for line in open(input_filename):
            count_substrings_trie(line, trie)
    trie.persist()

    results = filter_results(trie)
    del trie
    results = sort_results(results)

    for substring, amount in results:
        print(json.dumps([substring, amount], ensure_ascii=False))

if __name__ == '__main__':
    main()
