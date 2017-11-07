#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; change main monitor from windows to linux
F4::
    Run nircmdc monitor off ; monitor will look for another input
    Sleep 1000
    Run taskkill /im nircmdc.exe /f
    Return

; mhk
*~SC07B::
    IniRead, VfioCredentials, conf.ini, Vfio, Credentials
    Run, curl --user %VfioCredentials% "http://es.lan:9888/voip?do=press",, Hide
    KeyWait, SC07B
    Run, curl --user %VfioCredentials% "http://es.lan:9888/voip?do=release",, Hide
    Return
