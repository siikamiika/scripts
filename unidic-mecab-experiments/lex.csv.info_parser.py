#!/usr/bin/env python3

import json

ENTRY_FORMAT = [
    'pos',
    'pos2',
    'pos3',
    'pos4',
    'inflection_type',
    'inflection_form',
]

def entry(line):
    return dict(zip(ENTRY_FORMAT, line.split(',')[4:]))


def main():
    unidic_info = dict((info, set()) for info in ENTRY_FORMAT)
    lex = open('lex.csv', encoding='utf-8')
    for line in lex:
        line_entry = entry(line)
        for info in line_entry:
            unidic_info[info].add(line_entry[info])
    for info in unidic_info:
        unidic_info[info] = sorted(list(unidic_info[info]))
        try:
            unidic_info[info].remove('*')
        except:
            pass
    with open('info.json', 'w') as info:
        json.dump(unidic_info, info)

if __name__ == '__main__':
    main()
