#!/usr/bin/env python3
import pynput

keyboard_controller = pynput.keyboard.Controller()

# lol
multiplier_keys = {
    3: pynput.keyboard.KeyCode.from_vk(0x53), # numpad 1
    4: pynput.keyboard.KeyCode.from_vk(0x54), # numpad 2
    5: pynput.keyboard.KeyCode.from_vk(0x55), # numpad 3
    6: pynput.keyboard.KeyCode.from_vk(0x57), # numpad 5
    7: pynput.keyboard.KeyCode.from_vk(0x59), # numpad 7
    8: pynput.keyboard.KeyCode.from_vk(0x5b), # numpad 8
    9: pynput.keyboard.KeyCode.from_vk(0x5c), # numpad 9
}

def on_scroll(x, y, dx, dy):
    # /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h
    if dx > 0:
        key = pynput.keyboard.KeyCode.from_vk(0x56) # numpad 4
    elif dx < 0:
        key = pynput.keyboard.KeyCode.from_vk(0x58) # numpad 6

    amount_left = abs(dx)
    while amount_left:
        multiplier_key = None
        if amount_left in multiplier_keys:
            multiplier_key = multiplier_keys[amount_left]
            amount_left = 0
        elif amount_left > max(multiplier_keys):
            multiplier_key = multiplier_keys[max(multiplier_keys)]
            amount_left -= max(multiplier_keys)
        else:
            amount_left -= 1

        if multiplier_key:
            keyboard_controller.press(multiplier_key)
            keyboard_controller.release(multiplier_key)

        keyboard_controller.press(key)
        keyboard_controller.release(key)

with pynput.mouse.Listener(on_scroll=on_scroll) as listener:
    listener.join()
