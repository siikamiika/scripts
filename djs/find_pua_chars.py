#!/usr/bin/env python3

import sys

def main():
    read = set()
    for filename in sys.argv[1:]:
        input_file = open(filename, 'r', encoding='utf-8')
        for line in input_file:
            for c in line:
                if 57524 <= ord(c) <= 57543:
                    read.add(ord(c))
        input_file.close()
    
    for c in sorted(read):
        print(c)

if __name__ == '__main__':
    main()
