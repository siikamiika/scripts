#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


^!Space::
ControlSend,, {Space}, ahk_class mpv
return

^!Up::
ControlSend,, {0}, ahk_class mpv
return

^!Down::
ControlSend,, {9}, ahk_class mpv
return

