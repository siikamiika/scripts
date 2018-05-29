#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; globals
IniRead, VfioCredentials, conf.ini, Vfio, Credentials
; global AudioPID := -1
global FunctionKeysOn := False
global RemoteKeyboardLaunchTime := -1

; init
PrintLn(VfioCredentials)
OnExit("CloseConnection")

; functions
PrintLn(String) {
    FileAppend, %String%`n, *, UTF-8
}

EscapeText(String) {
    String := StrReplace(String, "\", "\\")
    String := StrReplace(String, "`n", "\n")
    String := StrReplace(String, " ", "\s")
    Return String
}

CloseConnection() {
    PrintLn("quit")
}

; hotkeys
; SC001::
;     FunctionKeysOn := !FunctionKeysOn
;     If (FunctionKeysOn) {
;         SoundPlay, %A_WinDir%\Media\Windows Hardware Remove.wav
;     } Else {
;         SoundPlay, %A_WinDir%\Media\Windows Hardware Insert.wav
;     }
;     Return

*SC04F::
    ; If (GetKeyState("SC07B", "P") or FunctionKeysOn) {
    ;     Send, {Blind}{F1}
    ;     Return
    ; }
    Return

*SC050::
    ; If (GetKeyState("SC07B", "P") or FunctionKeysOn) {
    ;     Send, {Blind}{F2}
    ;     Return
    ; } Else If (A_TickCount - RemoteKeyboardLaunchTime > 500) {
    ;     RemoteKeyboardLaunchTime := A_TickCount
    ;     Run, remotekeyboard.bat,, Hide
    ; }
    Return

; *Pause::
; *SC04F::
;     If (A_TickCount - RemoteKeyboardLaunchTime > 500) {
;         RemoteKeyboardLaunchTime := A_TickCount
;         Run, remotekeyboard.bat,, Hide
;     }
;     Return

; toggle audio
; F3::
;     If (AudioPID != -1) {
;         SoundPlay, %A_WinDir%\Media\Windows Hardware Remove.wav
;         Sleep, 500
;         Process, Close, %AudioPID%
;         AudioPID := -1
;     } Else {
;         Run, python.exe stream-pyaudio.py,, Hide, AudioPID
;         Sleep, 500
;         SoundPlay, %A_WinDir%\Media\Windows Hardware Insert.wav
;     }
;     Return

; change main monitor from windows to linux
; *F3::
; *F4::
*SC04B::
    ; If (GetKeyState("SC07B", "P") or GetKeyState("LAlt", "P") or FunctionKeysOn) {
    ;     FunctionKey := SubStr(A_ThisHotkey, 2)
    ;     Send, {Blind}{%FunctionKey%}
    ;     Return
    ; }
    Run, nircmdc monitor off,, Hide ; monitor will look for another input
    Sleep 1000
    Run, taskkill /im nircmdc.exe /f,, Hide
    Return

; mhk
; *~SC07B::
;     PrintLn("keydown 102")
;     KeyWait, SC07B
;     PrintLn("keyup 102")
;     Return

; GoldenDict
*!~LButton::
    KeyWait, LButton
    If (!GetKeyState("LWin", "P")) {
        Return
    }
    Send, ^c
    Sleep, 50
    String := EscapeText(Clipboard)
    PrintLn("clipboard_copy " String)
    PrintLn("keydown 37")
    PrintLn("keydown 102")
    PrintLn("keyup 102")
    PrintLn("keyup 37")
    Return

; codepoint
^#c::
    Send, ^c
    Sleep, 50
    String := EscapeText(Clipboard)
    PrintLn("clipboard_copy " String)
    PrintLn("keydown 37")
    PrintLn("keydown 133")
    PrintLn("keydown 54")
    PrintLn("keyup 54")
    PrintLn("keyup 37")
    PrintLn("keyup 133")
    Return

AppsKey::
    Run, python paste.py clipboard,, Hide
    Return

+AppsKey::
    Run, python paste.py primary,, Hide
    Return
