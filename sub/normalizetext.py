#!/usr/bin/env python3

import unicodedata
import sys
import glob

def normalize_file(fn):
    with open(fn, 'r', encoding='utf-8') as f:
        tmp = f.read()
    if tmp[0] == '\ufeff':
            tmp = tmp[1:]
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(unicodedata.normalize('NFKC', tmp))

def main():
    if len(sys.argv) == 2:
        fn = sys.argv[1]
        normalize_file(fn)
    elif len(sys.argv) == 1:
        files  = glob.glob('*.srt')
        print('normalize files:')
        print(files)
        srs = input('srs? (y/n): ')
        if srs == 'y':
            for fn in files:
                normalize_file(fn)
                print(fn)

if __name__ == '__main__':
    main()
