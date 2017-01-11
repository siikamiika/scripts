#!/usr/bin/env python3

import json

with open('info.json', 'r') as f:
    info = json.load(f)

with open('humanreadable.txt', 'w') as hr:
    output = []
    for i in info:
        output.append(i)
        output += info[i]
    hr.write('\n'.join(output))
