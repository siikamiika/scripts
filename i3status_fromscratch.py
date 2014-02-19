#!/usr/bin/env python3
import sys
import subprocess
import json
import socket
import time
from datetime import datetime
# from shutil import disk_usage
import re

def write_line(text):
    print(text)
    sys.stdout.flush()

def mpd(old):
    try:
        old.send(b'currentsong\n')
        return old.recv(1024).decode(), old
    except:
        try:
            mpd = socket.socket()
            mpd.connect(('localhost', 6600))
            mpd.recv(1024)
            mpd.send(b'currentsong\n')
            return mpd.recv(1024).decode(), mpd
        except:
            return None, None

def song_name(mpd_currentsong):
    try:
        song = dict(l.split(': ') for l in mpd_currentsong.splitlines()[:-1])
        if song.get('Title'):
            if song.get('Artist'):
                return '{0} - {1}'.format(song['Artist'], song['Title'])
            else:
                return song['Title']
    except:
        return

write_line('{"version":1}')
write_line('[')
write_line('[{"full_text": "initializing"}]')
mpd_connection = None
playing = None
song_parts = []
good, bad = '#05A600', '#A60700'
SLEEP = 2
time.sleep(SLEEP - (time.time() % SLEEP))

while True:
    if subprocess.getoutput('pgrep 3lock'):
        SLEEP = 30
    else:
        SLEEP = 2
    parts = []

    # mpd current song
    currentsong, mpd_connection = mpd(mpd_connection)
    playing_tmp = playing
    playing = song_name(currentsong)
    if playing:
        if playing == playing_tmp:
            if not song_parts:
                song_parts = re.findall('.{30}|.+?$', playing)
        else:
            song_parts = re.findall('.{30}|.+?$', playing)
        parts.append({
            'full_text': song_parts.pop(0).ljust(30), 'color': '#285577'
        })

    # mpd volume
    vol = subprocess.getoutput('mpc volume').split(': ')[1]
    if vol != 'n/a':
        parts.append({'full_text': '♪'+vol, 'color': '#285577'})

    # # disk usage
    # G = 1024**3
    # root = disk_usage('/')
    # win7 = disk_usage('/media/win7/')
    # root_color, win7_color = [
    #         good if d[2]*10 > d[0] else bad
    #         for d in [root, win7]
    #     ]
    # parts.append({'full_text': '/', 'color': '#565656'})
    # parts.append({
    #     'full_text': '{0:.1f} GiB'.format(root[2]/G), 'color': root_color
    # })
    # parts.append({'full_text': '/media/win7/', 'color': '#565656'})
    # parts.append({
    #     'full_text': '{0:.1f} GiB'.format(win7[2]/G), 'color': win7_color
    # })

    # cpu temp
    raw_temp = subprocess.getoutput(
            'cat /sys/class/thermal/thermal_zone0/temp'
        )
    tmp = int(raw_temp[:-3])
    cpu_color = good if tmp < 50 else bad
    parts.append({
        'full_text': 'cpu: {} °C'.format(raw_temp[:-3]), 'color': cpu_color
    })

    # date and time
    parts.append({
        'full_text': datetime.now().strftime("%a %d %b %Y %H:%M:%S")
    })

    # volume
    parts.append({
        'full_text': subprocess.getoutput('pamixer --get-volume')+'%'
    })

    write_line(','+json.dumps(parts))
    time.sleep(SLEEP - (time.time() % SLEEP))
