#!/usr/bin/env python3

import re

ENTRY_FORMAT = [
    'pos',
    'pos2',
    'pos3',
    'pos4',
    'inflection_type',
    'inflection_form',
    'lemma_reading',
    'lemma',
    '_',
    'reading',
    '_',
    'orth_reading',
]


def remove_chouon(text):
    if not text:
        return ''
    t = []
    previous = ''
    for c in text:
        if c == 'ー':
            if previous in 'アカガサザタダナハバパマヤャラワ':
                t.append('ア')
            elif previous in 'イキギシジチヂニヒビピミリヰエケゲセゼテデネヘベペメレヱ':
                t.append('イ')
            elif previous in 'ウクグスズツヅヌフブプムユュルオコゴソゾトドノホボポモヨョロヲ':
                t.append('ウ')
            else:
                t.append('ー')
        else:
            t.append(c)
        previous = c
    return ''.join(t)

def entry(line):
    return dict(zip(ENTRY_FORMAT, line.split(',')[4:]))

pattern = re.compile(r'^下一段')

def main():
    maybe_potential = []
    lex = open('lex.csv', encoding='utf-8')
    for line in lex:
        line_entry = entry(line)
        if pattern.match(line_entry['inflection_type']) and line_entry['orth_reading'] and line_entry['lemma_reading'][-2:] != remove_chouon(line_entry['orth_reading'][-2:]):
            maybe_potential.append(line)
    with open('potentials.txt', 'w') as info:
        info.write(''.join(maybe_potential))

if __name__ == '__main__':
    main()
