#!/usr/bin/env python3
import sys
import glob

def convert_encoding(fn, frm, to):
    with open(fn, 'r', encoding=frm) as f:
        tmp = f.read()
    with open(fn, 'w', encoding=to) as f:
        f.write(tmp)

def main():
    files  = glob.glob('*'+sys.argv[1])
    frm = sys.argv[2]
    to = sys.argv[3]
    print('convert from {} to {}:'.format(frm, to))
    print(files)
    srs = input('srs? (y/n): ')
    if srs == 'y':
        for fn in files:
            convert_encoding(fn, frm, to)
            print(fn)

if __name__ == '__main__':
    main()
