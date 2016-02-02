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
SC07B & '::Key("Ä", "ä")
SC079 & a::Key("Ä", "ä")
SC07B & `;::Key("Ö", "ö")
SC079 & o::Key("Ö", "ö")
SC07B & [::Key("Å", "å")
SC079 & q::Key("Å", "å")


; navigation keys
SC079 & h:: Send, {Blind}{Left}
SC079 & j:: Send, {Blind}{Down}
SC079 & k:: Send, {Blind}{Up}
SC079 & l:: Send, {Blind}{Right}

SC079 & i:: Send, {Blind}{Insert}
SC079 & u:: Send, {Blind}{Delete}
SC079 & p:: Send, {Blind}{Home}
SC079 & `;:: Send, {Blind}{End}
SC079 & [:: Send, {Blind}{PgUp}
SC079 & ':: Send, {Blind}{PgDn}


; caps
+CapsLock::CapsLock
Capslock::Esc

; backspace
SC070:: Send, {BS}
^SC070::Send, ^{BS}

; change layout
~!+2::Run, thumbshift.ahk
~!+3::Run, rusphonetic.ahk
