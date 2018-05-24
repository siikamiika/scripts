#!/usr/bin/env python3

import os
from os.path import dirname, realpath
from subprocess import Popen, DEVNULL
from evdev import InputDevice
from evdev.ecodes import *

os.chdir(dirname(realpath(__file__)))

# blacklist this for xorg
DEVICE = '/dev/input/by-id/usb-Cypress_Cypress_USB_Keyboard___PS2_Mouse-event-kbd'

class MacroPad(object):

    def __init__(self, device_path):
        self.device_path = device_path
        self.device = None

        self.keys_down = set()
        self.handlers = dict()

    def add_handler(self, key, handler):
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)

    def start_loop(self):
        self.device = InputDevice(self.device_path)
        for event in self.device.read_loop():
            if event.type == EV_KEY:
                # add/remove keydown
                if event.value == 1:
                    self.keys_down.add(event.code)
                elif event.value == 0:
                    try:
                        self.keys_down.remove(event.code)
                    except KeyError:
                        pass
                # run macro
                if event.code in self.handlers:
                    self._run_macros(event.code, event.value)

    def _run_macros(self, key_code, key_state):
        handlers = self.handlers[key_code]
        active_modifiers = set()
        for handler in handlers:
            if isinstance(handler, dict) and 'modifiers' in handler:
                active_modifiers |= set(handler['modifiers'])

        for macro in handlers:
            modifiers = set()
            listeners = [None, None, None]

            if isinstance(macro, dict):
                if 'modifiers' in macro:
                    modifiers |= set(macro['modifiers'])
                if 'listeners' in macro:
                    if isinstance(macro['listeners'], str):
                        listeners[1] = macro['listeners']
                    else:
                        listeners = macro['listeners']
            elif isinstance(macro, str):
                listeners[1] = macro
            else:
                listeners = macro

            # key is held, add key to modifiers
            if key_state > 0:
                modifiers |= {key_code}
            # default
            modifier_match = True
            # active modifiers for key are held, use exact match
            if self.keys_down & active_modifiers:
                modifier_match = modifiers == self.keys_down
            # use loose match
            elif active_modifiers:
                modifier_match = modifiers <= self.keys_down

            if listeners[key_state] and modifier_match:
                Popen(listeners[key_state], shell=True, stdout=DEVNULL, stderr=DEVNULL)

def main():
    macro_pad = MacroPad(DEVICE)
    # numpad keys:
    # KEY_KP0, KEY_KP1, KEY_KP2, KEY_KP3, KEY_KP4, KEY_KP5, KEY_KP6, KEY_KP7, KEY_KP8, KEY_KP9,
    # KEY_KPDOT, KEY_KPENTER, KEY_KPPLUS, KEY_KPMINUS, KEY_KPASTERISK, KEY_KPSLASH, KEY_NUMLOCK

    # configuration

    # numpad 1 press when numpad 0 is held
    macro_pad.add_handler(KEY_KP1, dict(
        modifiers={KEY_KP0},
        listeners='ffmpeg -f lavfi -i "sine=frequency=500:duration=0.5" -f wav - | mpv -' # press only
    ))
    # numpad 2 release/press/hold when numpad 0 is held
    macro_pad.add_handler(KEY_KP2, dict(
        modifiers={KEY_KP0},
        listeners=(
            'ffmpeg -f lavfi -i "sine=frequency=500:duration=0.1" -f wav - | mpv -',  # release
            'ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.1" -f wav - | mpv -', # press
            'ffmpeg -f lavfi -i "sine=frequency=2000:duration=0.1" -f wav - | mpv -'  # hold (repeat)
        )
    ))
    # numpad 1 press only
    macro_pad.add_handler(KEY_KP1, 'ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.5" -f wav - | mpv -')
    # numpad 3 press only
    macro_pad.add_handler(KEY_KP3, 'ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.5" -f wav - | mpv -')

    # start
    macro_pad.start_loop()

if __name__ == '__main__':
    main()
