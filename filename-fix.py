#!/usr/bin/env python3 

import os
import sys

REPLACEMENTS = {}

for c in 'öäåÖÄÅ':
    REPLACEMENTS[c.encode('utf-8').decode('latin-1')] = c

def fix_path(path):
    for r in REPLACEMENTS:
        path = path.replace(r, REPLACEMENTS[r])
    return path

def rename_path(path, subdir):
    new_path = fix_path(path)
    if new_path != path:
        user_input = input('{} --> {} (Y/n): '.format(path, new_path))
        if user_input == '' or user_input == 'Y':
            src = os.path.join(subdir, path)
            dst = os.path.join(subdir, new_path)
            try:
                os.rename(src, dst)
            except FileExistsError:
                if input('{} exists. Continue? (Y/n)'.format(dst)) in ['', 'Y']:
                    pass
                else:
                    sys.exit()

def main():
    for subdir, dirs, files in os.walk(sys.argv[1]):
        print(subdir)
        for path in files + dirs:
            rename_path(path, subdir)

if __name__ == '__main__':
    main()
