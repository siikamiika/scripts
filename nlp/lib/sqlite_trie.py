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
        self._run_sql(
            '''
            WITH RECURSIVE suffix_path (id, parent_id, char, count, depth, max_id, updated) AS (
                SELECT
                    wt.id,
                    wt.parent_id,
                    wt.char,
                    wt.count,
                    0 AS depth,
                    (SELECT MAX(id) FROM wordcount_trie) AS max_id,
                    FALSE AS updated
                FROM wordcount_trie AS wt
                WHERE id = :root_id

                UNION ALL

                SELECT
                    COALESCE(wt.id, s.max_id + 1) AS id,
                    s.id AS parent_id,
                    SUBSTR(:string, s.depth + 1, 1) AS char,
                    (
                        COALESCE(wt.count, 0)
                        + (CASE WHEN s.depth = LENGTH(:string) - 1 THEN 1 ELSE 0 END)
                    ) AS count,
                    s.depth + 1 AS depth,
                    COALESCE(MAX(wt.id, s.max_id), s.max_id + 1) AS max_id,
                    (wt.id IS NULL OR s.depth = LENGTH(:string) - 1) AS updated
                FROM suffix_path AS s
                LEFT JOIN wordcount_trie AS wt ON (
                    s.id = wt.parent_id
                    AND wt.char = SUBSTR(:string, s.depth + 1, 1)
                )
                WHERE s.depth < LENGTH(:string)
            )
            REPLACE INTO wordcount_trie
            SELECT id, parent_id, char, count
            FROM suffix_path
            WHERE updated
            ''',
            {'root_id': self._root[0], 'string': string}
        )

    def find(self, string):
        pivot = self._root
        for char in string:
            pivot = self._get_child(pivot[0], char)
            if pivot is None:
                return None
        return self._from_root(pivot)

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

    def phrase_segment(self, phrase):
        result = self._run_sql(
            f'''
            WITH RECURSIVE substr_suffixes (id, parent_id, suffix, count, depth) AS (
                SELECT wt.*, 0 AS depth
                FROM wordcount_trie AS wt
                WHERE id = :root_id

                UNION ALL

                SELECT wt.*, s.depth + 1
                FROM substr_suffixes AS s, wordcount_trie AS wt
                WHERE wt.parent_id = s.id
                    AND s.depth < LENGTH(:string)
                    AND wt.char = SUBSTR(:string, s.depth + 1, 1)
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
            {'root_id': self._root[0], 'string': phrase}
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
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                char TEXT,
                count INTEGER DEFAULT 0
            )
        ''')
        self._run_sql('CREATE INDEX IF NOT EXISTS parent ON wordcount_trie (parent_id)')
        self._run_sql('CREATE UNIQUE INDEX IF NOT EXISTS char_parent ON wordcount_trie (char, parent_id)')
        if len(self._run_sql('SELECT * FROM wordcount_trie WHERE id = 1')) == 0:
            self._run_sql('INSERT INTO wordcount_trie (id, parent_id, char, count) VALUES (1, NULL, NULL, 0)')

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

    def __iter__(self):
        yield from self.suffixes()
