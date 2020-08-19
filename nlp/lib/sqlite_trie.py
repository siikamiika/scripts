#!/usr/bin/env python3

import os
import sqlite3

class WordCountTrieSqlite:
    def __init__(self, path, conn=None, cursor=None, root=None):
        self._path = path
        if conn is None:
            self._conn = sqlite3.connect(':memory:')
            self._cursor = self._conn.cursor()
            self._ensure_table()
            self._root = self._get_initial_root()
        else:
            self._conn = conn
            self._cursor = cursor
            self._root = root

    def add(self, string):
        #  0   1          2     3
        # (id, parent_id, char, count)
        if len(string) == 0: return
        pivot = self._root
        for char in string:
            pivot = self._get_child(pivot[0], char) or self._create_child(pivot[0], char)
        self._increment_wordcount(pivot[0])

    def find(self, string):
        pivot = self._root
        for char in string:
            pivot = self._get_child(pivot[0], char)
            if pivot is None:
                return None
        return self._from_root(pivot)

    def count(self):
        return self._root[3]

    def deduped_suffixes(self, min_length=None, max_length=None):
        prev_suffix = None
        prev_word_count = None
        word_count = None
        for suffix, word_count in self.suffixes(min_length, max_length):
            if prev_suffix is None:
                prev_suffix, prev_word_count = suffix, word_count
                continue
            if prev_word_count != word_count:
                yield prev_suffix, prev_word_count
            prev_suffix, prev_word_count = suffix, word_count
        if prev_word_count is not None:
            yield prev_suffix, prev_word_count

    def suffixes(self, min_length=None, max_length=None):
        # depth first
        stack = [iter(self._get_children(self._root[0]))]
        word = []
        while True:
            pivot = stack[-1]
            try:
                if max_length is not None and len(stack) > max_length:
                    raise StopIteration
                id, _, char, word_count = next(pivot)
                word.append(char)
                if (min_length is None or len(stack) >= min_length) and word_count > 0:
                    yield ''.join(word), word_count
                stack.append(iter(self._get_children(id)))
            except StopIteration:
                if len(stack) == 1:
                    break
                stack.pop()
                word.pop()

    def suffixes_cte_test(self, min_length=None, max_length=None):
        if (min_length is not None and min_length < 1) or (max_length is not None and max_length < 1):
            raise Exception('Out of range: (min_length={}, max_length={})'.format(min_length, max_length))

        return self._run_sql(
            '''
            WITH RECURSIVE suffixes (id, parent_id, suffix, count, depth) AS (
                SELECT wt.id, wt.parent_id, '' AS suffix, wt.count, 0 AS depth
                FROM wordcount_trie AS wt
                WHERE id = ? -- root id

                UNION ALL

                SELECT wt.id, wt.parent_id, (s.suffix || wt.char) AS suffix, wt.count, s.depth + 1
                FROM suffixes AS s, wordcount_trie AS wt
                WHERE wt.parent_id = s.id
            )
            SELECT s.suffix, s.count
            FROM suffixes AS s
            WHERE s.count > 0
                AND COALESCE(s.depth >= COALESCE(?, 1), TRUE)
                AND COALESCE(s.depth <= ?, TRUE)
            ''',
            [
                self._root[0],
                min_length,
                max_length
            ]
        )

    def phrase_segment(self, phrase):
        result = self._run_sql(
            f'''
            WITH RECURSIVE substr_suffixes (id, parent_id, suffix, count, depth) AS (
                SELECT wt.*, 0 AS depth
                FROM wordcount_trie AS wt
                WHERE id = ? -- root id

                UNION ALL

                SELECT wt.*, s.depth + 1
                FROM substr_suffixes AS s, wordcount_trie AS wt
                WHERE wt.parent_id = s.id
                    AND s.depth < ?
                    AND wt.char = SUBSTR(?, s.depth + 1, 1)
            )
            SELECT
                ss.depth,
                ss.suffix,
                (ss.count / (
                    SELECT AVG(wt.count)
                    FROM wordcount_trie wt
                    WHERE wt.parent_id = ss.parent_id
                        AND wt.id != ss.id
                )) AS relative_count
            FROM substr_suffixes AS ss
            WHERE ss.depth > 0
            ORDER BY relative_count DESC
            LIMIT 1
            ''',
            [self._root[0], len(phrase), phrase]
        )
        if len(result) == 0:
            return 1
        return result[0][0]

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

    def _from_root(self, root):
        return WordCountTrieSqlite(self._path, self._conn, self._cursor, root)

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

    def _get_initial_root(self):
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
        yield from self.suffixes()
