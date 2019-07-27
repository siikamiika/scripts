#!/usr/bin/env python3
import pynput

keyboard_controller = pynput.keyboard.Controller()

def on_scroll(x, y, dx, dy):
    # /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h
    if dx > 0:
        key = pynput.keyboard.KeyCode.from_vk(0x56) # numpad 4
    elif dx < 0:
        key = pynput.keyboard.KeyCode.from_vk(0x58) # numpad 6
    for _ in range(abs(dx)):
        keyboard_controller.press(key)
        keyboard_controller.release(key)

with pynput.mouse.Listener(on_scroll=on_scroll) as listener:
    listener.join()
