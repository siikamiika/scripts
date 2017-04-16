#!/usr/bin/env python3

import csv
import itertools
import sys

def is_kanji(c):
    return (0x4e00 <= ord(c) <= 0x9faf
        or 0xf900 <= ord(c) <= 0xfaff
        or 0x20000 <= ord(c) <= 0x2a6df
        or 0x2a700 <= ord(c) <= 0x2b73f
        or 0x2b740 <= ord(c) <= 0x2b81f
        or 0x2b820 <= ord(c) <= 0x2ceaf
        or 0x2f800 <= ord(c) <= 0x2f800
        or ord(c) in [0x3005, 0x3006])

class EntryIndexes(object):

    def __init__(self, headword, describe1, describe2, original_spelling, original_spelling_explanation, historical):
        # あい‐きょう
        # 口(くち)が減らない <-- 口 reading is くち, maps to 口(くち)が減らない and くちが減らない
        # あらわ・す <-- ignore ・
        # いい‐だし
        # 口(くち)が干上(ひあ)が・る
        self.headword = headword.replace('・', '').replace('‐', '')
        # has some extra PUA symbols to indicate non-jouyou etc.
        # ignore for now
        self.describe1 = describe1
        # no extra symbols
        # 哀叫
        # 嗚呼／噫
        # RSウイルス
        # グッゲンハイム美術館
        # 勲〔勳〕
        # 御断り〔断わり〕
        # 行い〔行ない〕
        # 現す〔現わす〕／表す〔表わす〕／顕す
        # 言（い）出し <-- optional い; maps to 言い出し and 言出し
        self.describe2 = describe2
        # (ドイツ)Kur
        # (ドイツ)Chrom／(フランス)chrome
        # Cromwell
        self.original_spelling = original_spelling
        self.original_spelling_explanation = original_spelling_explanation
        # あい‐きょう,哀叫,哀叫,,,‐ケウ <-- this
        self.historical = historical
        self.indexes = []
        self._parse_indexes()

    def _parse_indexes(self):
        self.indexes += self._parse_headwords()
        self.indexes += self._parse_describe2()
        self.indexes += self._parse_original_spelling()

    def _parse_headwords(self):
        readings = []
        word_start = None
        word_end = None
        reading_start = None
        in_reading = False
        for i, c in enumerate(self.headword):
            if c == '(':
                word_end = i
                reading_start = i + 1
                in_reading = True
                continue
            if c == ')':
                if word_start == None:
                    print(self.headword)
                readings.append((word_start, i, word_start, word_end, reading_start, i))
                word_start = None
                word_end = None
                reading_start = None
                in_reading = False
                continue
            if not in_reading and not is_kanji(c):
                word_start = None
                continue
            if is_kanji(c) and word_start == None:
                word_start = i
                continue
        
        if not readings:
            return [self.headword]

        headwords = []
        for i in range(len(readings) + 1):
            for c in itertools.combinations(range(len(readings)), i) if i > 0 else [()]:
                end = -1
                output = []
                for j in range(len(readings)):
                    # add what's between previous reading and this reading
                    output.append(self.headword[end + 1:max(readings[j][0], 0)])
                    if j in c: # then add word
                        output.append(self.headword[readings[j][2]:readings[j][3]])
                    else: # add reading
                        output.append(self.headword[readings[j][4]:readings[j][5]])
                    end = readings[j][1]
                # tail
                output.append(self.headword[readings[-1][1] + 1:])
                headwords.append(''.join(output))

        return headwords

    def _parse_describe2(self):
        def parse_optional(text):
            optionals = []
            optional_start = None
            for i, c in enumerate(text):
                if c == '（':
                    optional_start = i
                    continue
                if c == '）':
                    optionals.append((optional_start, i))

            if not optionals:
                return [text]

            combinations = []
            for i in range(-1, len(optionals)):
                end = -1
                output = []
                for j in range(len(optionals)):
                    # add what's between previous optional and this optional
                    output.append(text[end + 1:max(optionals[j][0], 0)])
                    if j <= i: # then add optional
                        output.append(text[optionals[j][0] + 1:optionals[j][1]])
                    end = optionals[j][1]
                # tail
                output.append(text[optionals[-1][1] + 1:])
                combinations.append(''.join(output))

            return combinations


        describe2 = []
        for describe in self.describe2.split('／'):                
            if describe:
                if '〔' in describe:
                    for d in describe.split('〔'):
                        describe2 += parse_optional(d.strip('〕'))
                else:
                    describe2 += parse_optional(describe)

        return describe2

    def _parse_original_spelling(self):
        original_spellings = []
        for original_spelling in self.original_spelling.split('／'):
            if original_spelling:
                original_spellings.append(original_spelling.split(')')[-1])

        return original_spellings


def test():
    test = EntryIndexes('口(くち)が干上(ひあ)が・る', '', '', '', '', '')
    assert(set(test.indexes) == {'くちがひあがる', '口がひあがる', 'くちが干上がる', '口が干上がる'})
    test2 = EntryIndexes('あ', '', '', '', '', '')
    assert(set(test2.indexes) == {'あ'})
    test3 = EntryIndexes('口(くち)が減らない', '', '', '', '', '')
    assert(set(test3.indexes) == {'くちが減らない', '口が減らない'})
    test4 = EntryIndexes('', '', '言（い）出し', '', '', '')
    assert(set(test4.indexes) == {'', '言出し', '言い出し'})
    test5 = EntryIndexes('', '', '現す〔糞（わ）す〕／表す〔表わす〕／顕す', '', '', '')
    assert(set(test5.indexes) == {'', '現す', '糞す', '糞わす', '表す', '表わす', '顕す'})
    test6 = EntryIndexes('', '', '', '(ドイツ)Chrom／(フランス)chrome', '', '')
    assert(set(test6.indexes) == {'', 'Chrom', 'chrome'})

def get_indexes(row):
    return EntryIndexes(row[2], row[3], row[4], row[5], row[6], row[7]).indexes

def main():
    test()
    input_file = open(sys.argv[1], 'r', encoding='utf-8')
    input_reader = csv.reader(input_file)
    output_file = open(sys.argv[2], 'w', encoding='utf-8')
    output_writer = csv.writer(output_file)
    output = dict()
    for row in input_reader:
        item_id = row[0]
        indexes = get_indexes(row)
        for index in indexes:
            if not output.get(index):
                output[index] = []
            output[index].append(item_id)
    for index in sorted(output):
        output_writer.writerow([index, '|'.join(list(set(output[index])))])
    input_file.close()
    output_file.close()

if __name__ == '__main__':
    main()
