#!/usr/bin/env python3

ENTRY_FORMAT = [
    '_',
    '_',
    '_',
    '_',
    '_',
    '_',
    '_',
    'lemma',
]

def get_lemma(line):
    return dict(zip(ENTRY_FORMAT, line.split(',')[4:]))['lemma']

def main():
    jmdict = JMdict_e()
    lemmas = set()
    potentials = open('potentials.txt', encoding='utf-8')
    for line in potentials:
        lemmas.add(get_lemma(line))
    lemmas = list(lemmas)
    with open('maybe_potential_lemmas.txt', 'w') as info:
        info.write('\n'.join(lemmas))

if __name__ == '__main__':
    main()
