#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; globals
IniRead, VfioCredentials, conf.ini, Vfio, Credentials
global AudioPID := -1

; init
PrintLn(VfioCredentials)
OnExit("CloseConnection")

; functions
PrintLn(String) {
    FileAppend, %String%`n, *, UTF-8
}

CloseConnection() {
    PrintLn("quit")
}

; hotkeys
; toggle audio
F3::
    If (AudioPID != -1) {
        SoundPlay, %A_WinDir%\Media\Windows Hardware Remove.wav
        Sleep, 500
        Process, Close, %AudioPID%
        Process, Close, linco.exe
        AudioPID := -1
    } Else {
        Run, python.exe stream-linco.py,, Hide, AudioPID
        Sleep, 500
        SoundPlay, %A_WinDir%\Media\Windows Hardware Insert.wav
    }
    Return

; change main monitor from windows to linux
F4::
    Run, nircmdc monitor off,, Hide ; monitor will look for another input
    Sleep 1000
    Run, taskkill /im nircmdc.exe /f,, Hide
    Return

; mhk
*~SC07B::
    PrintLn("keydown 102")
    KeyWait, SC07B
    PrintLn("keyup 102")
    Return

AppsKey::
    Run, python paste.py clipboard,, Hide
    Return

+AppsKey::
    Run, python paste.py primary,, Hide
    Return
