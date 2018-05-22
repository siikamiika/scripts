#!/usr/bin/env python3

import os
from os.path import dirname, realpath
from subprocess import Popen, DEVNULL
from evdev import InputDevice
from evdev.ecodes import *

os.chdir(dirname(realpath(__file__)))

# blacklist this for xorg
DEVICE = '/dev/input/by-id/usb-Cypress_Cypress_USB_Keyboard___PS2_Mouse-event-kbd'

KEYS = {
    KEY_KP0: 'aplay /dev/urandom & sleep 2; killall aplay', # press only
    KEY_KP1: (
        'ffmpeg -f lavfi -i "sine=frequency=500:duration=0.1" -f wav - | mpv -',  # release
        'ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.1" -f wav - | mpv -', # press
        'ffmpeg -f lavfi -i "sine=frequency=2000:duration=0.1" -f wav - | mpv -'  # hold (repeat)
    ),
    KEY_KP2: './test.bash', # relative to script directory
    KEY_KP3: None,
    KEY_KP4: None,
    KEY_KP5: None,
    KEY_KP6: None,
    KEY_KP7: None,
    KEY_KP8: None,
    KEY_KP9: None,
    KEY_KPDOT: None,
    KEY_KPENTER: None,
    KEY_KPPLUS: None,
    KEY_KPMINUS: None,
    KEY_KPASTERISK: None,
    KEY_KPSLASH: None,
    KEY_NUMLOCK: None,
}

def run_macro(macro, key_state):
    if not macro:
        return

    if isinstance(macro, str):
        if key_state == 1:
            Popen(macro, shell=True)
    elif macro[key_state]:
        Popen(macro[key_state], shell=True, stdout=DEVNULL, stderr=DEVNULL)

def main():
    device = InputDevice(DEVICE)
    for event in device.read_loop():
        if event.type == EV_KEY and event.code in KEYS:
            run_macro(KEYS[event.code], event.value)

if __name__ == '__main__':
    main()
