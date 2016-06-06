#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

ControlSetText, Edit1, %1%, Concise Oxford English Dictionary (Eleventh Edition)
Sleep, 200
ControlClick, Button4, Concise Oxford English Dictionary (Eleventh Edition),,,,NA
Sleep, 200
ControlClick, Button2, Copy or print the entry