#!/usr/bin/env python3
"""
Toggle mute on a focused X application.
Does nothing if the focused application doesn't have a pulseaudio sink
input.
Bind this script on a hotkey with xbindkeys or similar.
"""
from subprocess import getoutput, call
import sys
from os.path import exists
from os import remove

raw_xprop = getoutput('xprop -root')
for l in raw_xprop.splitlines():
    if l.startswith('_NET_ACTIVE_WINDOW'):
        win_id = l.split()[-1]
        break
xprop_focused = getoutput('xprop -id '+win_id)
for l in xprop_focused.splitlines():
    if l.startswith('_NET_WM_PID'):
        pid = l.split()[-1]
inputs = getoutput('pacmd list-sink-inputs')
inputs = inputs.split('\n    index: ')
if len(inputs) <= 1:
    sys.exit()

def pid2input_id(input_info):
    lines = input_info.splitlines()
    input_id = lines[0]
    for l in lines:
        if l.startswith('\t\tapplication.process.id'):
            if l.split()[-1].strip('"') == pid:
                return input_id
    return '-1'


for i in inputs:
    input_id = pid2input_id(i)
    if input_id != '-1':
        break

if input_id == '-1':
    sys.exit()

else:
    fn = '/tmp/{}.muted'.format(input_id)
    if exists(fn):
        call(['pacmd', 'set-sink-input-mute', input_id, 'false'])
        remove(fn)
    else:
        open(fn, 'a').close()
        call(['pacmd', 'set-sink-input-mute', input_id, 'true'])

