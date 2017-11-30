#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Menu, Tray, Icon, en.ico

global key_027_mhk := {1: "Ö", 2: "ö"}
global key_028_mhk := {1: "Ä", 2: "ä"}
global key_027 := {1: ":", 2: "`;"}
global key_028 := {1: """", 2: "'"}
global vfio_hotkeys_started := False


Finnish(on) {
    if on {
        key_027 := {1: "Ö", 2: "ö"}
        key_028 := {1: "Ä", 2: "ä"}
        key_027_mhk := {1: ":", 2: "`;"}
        key_028_mhk := {1: """", 2: "'"}
        Hotkey, SC027, on
        Hotkey, +SC027, on
        Hotkey, SC028, on
        Hotkey, +SC028, on
    }
    else {
        key_027_mhk := {1: "Ö", 2: "ö"}
        key_028_mhk := {1: "Ä", 2: "ä"}
        Hotkey, SC027, off
        Hotkey, +SC027, off
        Hotkey, SC028, off
        Hotkey, +SC028, off
    }
    Return
}

Finnish(false)


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
SC028::Key(key_028[1], key_028[2])
+SC028::Key(key_028[1], key_028[2])
SC07B & SC028::Key(key_028_mhk[1], key_028_mhk[2])
SC079 & SC01E::Key(key_028_mhk[1], key_028_mhk[2])
SC027::Key(key_027[1], key_027[2])
+SC027::Key(key_027[1], key_027[2])
SC07B & SC027::Key(key_027_mhk[1], key_027_mhk[2])
SC079 & SC018::Key(key_027_mhk[1], key_027_mhk[2])
SC07B & SC01A::Key("Å", "å")
SC079 & SC010::Key("Å", "å")
; ...for Finnish keyboards
*SC056::Key("Ä", "ä")
*>!SC056::Key("Ö", "ö")
*>!SC01E::Key("Ä", "ä")
*>!SC018::Key("Ö", "ö")
*>!SC010::Key("Å", "å")


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
; ...for Finnish keyboards
FinnishNav(NavKey) {
    Modifiers := ""
    if (GetKeyState("LCtrl", "P")) {
        Modifiers = %Modifiers%^
    }
    if (GetKeyState("LAlt", "P")) {
        Modifiers = %Modifiers%!
    }
    if (GetKeyState("Shift", "P")) {
        Modifiers = %Modifiers%+
    }
    if (GetKeyState("LWin", "P")) {
        Modifiers = %Modifiers%#
    }
    Send, %Modifiers%{%NavKey%}
    Return
}
*>!SC023::FinnishNav("Left")
*>!SC024::FinnishNav("Down")
*>!SC025::FinnishNav("Up")
*>!SC026::FinnishNav("Right")

*>!SC017::FinnishNav("Insert")
*>!SC016::FinnishNav("Delete")
*>!SC019::FinnishNav("Home")
*>!SC027::FinnishNav("End")
*>!SC01A::FinnishNav("PgUp")
*>!SC028::FinnishNav("PgDn")
; workaround for lockscreen (conflicts with mhk+Win+L)
#SC027::
    RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Policies\System, DisableLockWorkstation, 0
    DllCall("LockWorkStation")
    Sleep, 1000
    RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Policies\System, DisableLockWorkstation, 1
    Return


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
!+1::
    Send, ^{F1} ; Precomposition | Ctrl F1 | Deactivate IME
    Menu, Tray, Icon, en.ico
    Finnish(false)
    Return
!+2::
    ;Run, thumbshift.ahk
    Send, ^{F2} ; DirectInput | Ctrl F2 | Activate IME
    Menu, Tray, Icon, en.ico
    Finnish(false)
    Return
!+3::
    Send, ^{F1}
    Menu, Tray, Icon, ru.ico
    Run, rusphonetic.ahk
    Return
!+4::
    Send, ^{F1}
    Menu, Tray, Icon, fi.ico
    Finnish(true)
    Return
F2::
    Run, remotekeyboard.bat,, Hide
    if (!vfio_hotkeys_started) {
        Run, vfio_hotkeys.bat,, Hide
        vfio_hotkeys_started = True
    }
    Return
F1::Return
