#!/usr/bin/env python3

import sys

DELIMITER = 9475

# kana
HIRAGANA_START = 0x3041
HIRAGANA_END = 0x3096
KATAKANA_START = 0x30A1
KATAKANA_END = 0x30FA
# kanji
CJK_IDEO_START = 0x4e00
CJK_IDEO_END = 0x9faf
# ascii
ASCII_UPPER_START = 0x41
ASCII_UPPER_END = 0x5a
ASCII_LOWER_START = 0x61
ASCII_LOWER_END = 0x7a
# latin1 supplement
LATIN1_SUPPLEMENT_1_START = 0xc0
LATIN1_SUPPLEMENT_1_END = 0xd6
LATIN1_SUPPLEMENT_2_START = 0xd8
LATIN1_SUPPLEMENT_2_END = 0xdf6
LATIN1_SUPPLEMENT_3_START = 0xf8
LATIN1_SUPPLEMENT_3_END = 0xff
# latin extended
LATIN_EXTENDED_START = 0x100
LATIN_EXTENDED_END = 0x24f
# cyrillic
CYRILLIC_START = 0x400
CYRILLIC_END = 0x4ff
# latin2 supplement
LATIN2_SUPPLEMENT_START = 0x1d00
LATIN2_SUPPLEMENT_END = 0x1fff


def is_kanji(c):
    return CJK_IDEO_START <= ord(c) <= CJK_IDEO_END

def is_kana(c):
    o = ord(c)
    if o > KATAKANA_END or o < HIRAGANA_START or HIRAGANA_END < o < KATAKANA_START:
        return False
    return True

def is_number(c):
    return 0x30 <= ord(c) <= 0x39

def is_ascii(c):
    return ASCII_UPPER_START <= ord(c) <= ASCII_UPPER_END or ASCII_LOWER_START <= ord(c) <= ASCII_LOWER_END

def is_latin1_supplement(c):
    for start, end in [(LATIN1_SUPPLEMENT_1_START, LATIN1_SUPPLEMENT_1_END),
        (LATIN1_SUPPLEMENT_2_START, LATIN1_SUPPLEMENT_2_END),
        (LATIN1_SUPPLEMENT_3_START, LATIN1_SUPPLEMENT_3_END)]:
        if start <= ord(c) <= end:
            return True
    return False

def is_latin_extended(c):
    return LATIN_EXTENDED_START <= ord(c) <= LATIN_EXTENDED_END

def is_cyrillic(c):
    return CYRILLIC_START <= ord(c) <= CYRILLIC_END

def is_latin2_supplement(c):
    return LATIN2_SUPPLEMENT_START <= ord(c) <= LATIN2_SUPPLEMENT_END

def is_text(c):
    return (is_kanji(c)
        or is_kana(c)
        or is_number(c)
        or is_ascii(c)
        or is_latin1_supplement(c)
        or is_latin_extended(c)
        or is_cyrillic(c)
        or is_latin2_supplement(c))

def main():
    read = dict()
    for filename in sys.argv[1:]:
        input_file = open(filename, 'r', encoding='utf-8')
        for line in input_file:
            line = line.strip().split(',')
            indexes = line[2].split(chr(DELIMITER))[1:]
            for index in indexes:
                for c in index:
                    if not is_text(c):
                        if not read.get(ord(c)):
                            print(c)
                            read[ord(c)] = [','.join(line), 0]
                        if read[ord(c)][1] < 10:
                            read[ord(c)][0] = ','.join(line)
                        read[ord(c)][1] += 1
        input_file.close()
    
    for c in sorted(read):
        print('{}\t{}\t{}\t{}\t{}'.format(c, hex(c), chr(c), read[c][1], read[c][0]))

if __name__ == '__main__':
    main()
