#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; Blind doesn't work with non-ascii
Key(upper, lower) {
    if GetKeyState("CapsLock", "T")
        if GetKeyState("Shift")
            Send, {%lower%}
        else
            Send, {%upper%}
    else if GetKeyState("Shift")
        Send, {%upper%}
    else
        Send, {%lower%}
    Return
}


; ÅåÄäÖö
SC07B & SC028::Key("Ä", "ä")
SC079 & SC01E::Key("Ä", "ä")
SC07B & SC027::Key("Ö", "ö")
SC079 & SC018::Key("Ö", "ö")
SC07B & SC01A::Key("Å", "å")
SC079 & SC010::Key("Å", "å")


; special characters
SC079 & -::
if GetKeyState("Shift")
    Send, —
else
    Send, –
Return
SC073::Send, <
Shift & SC073::Send, >
SC07B & SC073::Send, |
SC079 & SC073::Send, |


; navigation keys
SC079 & SC023:: Send, {Blind}{Left}
SC079 & SC024:: Send, {Blind}{Down}
SC079 & SC025:: Send, {Blind}{Up}
SC079 & SC026:: Send, {Blind}{Right}

SC079 & SC017:: Send, {Blind}{Insert}
SC079 & SC016:: Send, {Blind}{Delete}
SC079 & SC019:: Send, {Blind}{Home}
SC079 & SC027:: Send, {Blind}{End}
SC079 & SC01A:: Send, {Blind}{PgUp}
SC079 & SC028:: Send, {Blind}{PgDn}


; "numpad"
SC07B & SC024:: Send, 1
SC07B & SC025:: Send, 2
SC07B & SC026:: Send, 3
SC07B & SC016:: Send, 4
SC07B & SC017:: Send, 5
SC07B & SC018:: Send, 6


; caps
+CapsLock::CapsLock
Capslock::Esc

; backspace
SC070:: Send, {BS}
^SC070::Send, ^{BS}

; change layout
;~!+2::Run, thumbshift.ahk
~!+3::Run, rusphonetic.ahk
