# macropad

- create `/etc/X11/xorg.conf.d/00-ignore-ext-numpad.conf`
```
Section "InputClass"
	Identifier "external numpad"
	#MatchIsKeyboard "On"
	MatchProduct "HID 04f3:0635"
	Option "Ignore" "on"
EndSection
```

- add user to the input group:  `sudo usermod -a -G input siikamiika`
- relog (not reboot)
- install python-evdev: `sudo pacman -S python-evdev`
- configure `macropad.py`
- autostart `macropad.py`
