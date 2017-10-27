#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; change main monitor from windows to linux
F4::
    Send {F4}               ; xrandr HDMI on
    Sleep 1000
    Send {F2}               ; switch synergy to linux
    Run nircmdc monitor off ; monitor will look for another input
    Sleep 1000
    Run taskkill /im nircmdc.exe /f
    Return
