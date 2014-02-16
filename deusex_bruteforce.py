#!/usr/bin/env python3
"""
Linux only
Depends on: xte

Start script while pointing camera towards a keypad.

Set DIGITS to access code length and USE_OBJECT to
"Use object in world" keybind
"""
from subprocess import call
from time import sleep

DIGITS = 3
USE_OBJECT = 'e'

print('starting in 3')
sleep(3)

for i in range(10**DIGITS):
    call(['xte', 'key '+USE_OBJECT])
    attempt = str(i).rjust(DIGITS, '0')
    print(attempt)
    nums = list(attempt)
    for num in nums:
        call(['xte', 'key '+num])

    call(['xte', 'key Escape'])

