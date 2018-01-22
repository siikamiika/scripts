#!/usr/bin/env python3

import os
import sys
import random
import glob
import json


def path_to_source_name(path):
    basename = os.path.basename(path)
    source_name = os.path.splitext(basename)[0]
    return source_name


def get_file_handle(script_path, random_position):
    st_info = os.stat(script_path)
    script_length = st_info.st_size

    script_handle = open(script_path, 'rb')
    if random_position:
        script_handle.seek(random.randint(0, int(.98 * script_length)))
        script_handle.readline()

    return script_handle, script_length


def find_example_sentences(path, text, all_examples=False):
    scripts = glob.glob(path)
    random.shuffle(scripts)
    scripts = [{'path': s, 'start_pos': -1, 'handle': None} for s in scripts]

    results = []

    for script in scripts:
        print(f'Searching {script["path"]}...', file=sys.stderr)

        script_handle, script_length = get_file_handle(script['path'], True)
        script_pos = script_handle.tell()
        script['handle'], script['start_pos'] = script_handle, script_pos

        print(f'    Start at {script_pos} ({script_pos / script_length:.1%})...', file=sys.stderr)

        found = False

        for line in script_handle:
            line = line.decode('utf-8').strip()
            if text in line:
                found = True
                print(f'    Example sentence found: {line}', file=sys.stderr)
                source = path_to_source_name(script['path'])
                results.append((source, line))
                if not all_examples:
                    return results

        if not found:
            print('    Example sentence not found.', file=sys.stderr)

    random.shuffle(scripts)

    for script in scripts:
        print(f'Searching {script["path"]} again from the other side...', file=sys.stderr)

        script['handle'].seek(0)

        found = False

        for line in script['handle']:
            if script['handle'].tell() > script['start_pos']:
                if not found:
                    print('    Example sentence not found.', file=sys.stderr)
                break

            line = line.decode('utf-8').strip()
            if text in line:
                found = True
                print(f'    Example sentence found: {line}', file=sys.stderr)
                source = path_to_source_name(script['path'])
                results.append((source, line))
                if not all_examples:
                    return results

    if len(results) == 0:
        print(f'No example sentences for 「{text}」.', file=sys.stderr)

    return results


def main():
    path = sys.argv[1]
    text = sys.argv[2]

    if len(sys.argv) > 3 and '--all' in sys.argv[3:]:
        results = find_example_sentences(path, text, True)
    else:
        results = find_example_sentences(path, text)

    print(json.dumps(results, ensure_ascii=False))


if __name__ == '__main__':
    main()
