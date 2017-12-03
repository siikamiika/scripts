#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#Persistent
#MaxHotkeysPerInterval 999
#Include, AHKHID.ahk

; constants
;__________
WM_INPUT := 0x00FF

; globals
;________
IniRead, VfioCredentials, conf.ini, Vfio, Credentials
KeysDown := {}

; init
;_____
; create dummy gui for AHKHID
Gui, +LastFound
GuiHandle := WinExist()
Gui, Show, Hide
AHKHID_Register(1, 2, GuiHandle, RIDEV_INPUTSINK)

OnMessage(WM_INPUT, "InputMsg")

; disable mouse movement in this OS
BlockInput, MouseMove

; authenticate
PrintLn(VfioCredentials)

; common functions
;_________________
PrintLn(String) {
    FileAppend, %String%`n, *, UTF-8
}

EscapeText(String) {
    String := StrReplace(String, "\", "\\")
    String := StrReplace(String, "`n", "\n")
    String := StrReplace(String, " ", "\s")
    Return String
}

; mouse functions
;________________

InputMsg(wParam, lParam) {
    Local flags, MouseEvent
    Critical

    MouseEvent := {mouse_buttons: []}

    MouseEvent["x"] := AHKHID_GetInputInfo(lParam, II_MSE_LASTX)
    MouseEvent["y"] := AHKHID_GetInputInfo(lParam, II_MSE_LASTY)

    flags := AHKHID_GetInputInfo(lParam, II_MSE_BUTTONFLAGS)
    If (flags & RI_MOUSE_LEFT_BUTTON_DOWN)
        MouseEvent["mouse_buttons"].Push("left_down")
    If (flags & RI_MOUSE_LEFT_BUTTON_UP)
        MouseEvent["mouse_buttons"].Push("left_up")
    If (flags & RI_MOUSE_RIGHT_BUTTON_DOWN)
        MouseEvent["mouse_buttons"].Push("right_down")
    If (flags & RI_MOUSE_RIGHT_BUTTON_UP)
        MouseEvent["mouse_buttons"].Push("right_up")
    If (flags & RI_MOUSE_MIDDLE_BUTTON_DOWN)
        MouseEvent["mouse_buttons"].Push("middle_down")
    If (flags & RI_MOUSE_MIDDLE_BUTTON_UP)
        MouseEvent["mouse_buttons"].Push("middle_up")
    If (flags & RI_MOUSE_BUTTON_4_DOWN)
        MouseEvent["mouse_buttons"].Push("xbutton1_down")
    If (flags & RI_MOUSE_BUTTON_4_UP)
        MouseEvent["mouse_buttons"].Push("xbutton1_up")
    If (flags & RI_MOUSE_BUTTON_5_DOWN)
        MouseEvent["mouse_buttons"].Push("xbutton2_down")
    If (flags & RI_MOUSE_BUTTON_5_UP)
        MouseEvent["mouse_buttons"].Push("xbutton2_up")
    If (flags & RI_MOUSE_WHEEL) {
        WheelDelta := AHKHID_GetInputInfo(lParam, II_MSE_BUTTONDATA)
        if (WheelDelta > 0) {
            MouseEvent["mouse_buttons"].Push("wheel_up")
        } else if (WheelDelta < 0) {
            MouseEvent["mouse_buttons"].Push("wheel_down")
        }
    }

    ControlMouse(MouseEvent)
}

ControlMouse(MouseEvent) {
    ; work around some strange bug
    if (MouseEvent["mouse_buttons"].Length() > 1) {
        Return
    }

    x := MouseEvent["x"]
    y := MouseEvent["y"]
    if (x != 0 or y != 0 or MouseEvent["mouse_buttons"].Length() != 0) {
        MouseButtons := MouseEvent["mouse_buttons"][1]
        PrintLn("mouse " x "," y " " MouseButtons)
    }
}

; keyboard functions
;___________________
Key(AHKCode, Code) {
    global KeysDown
    if (KeysDown.hasKey(AHKCode)) {
        Return
    }
    KeysDown[AHKCode] := True
    PrintLn("keydown " Code)
}

KeyUp(AHKCode, Code) {
    global KeysDown
    AHKCode := SubStr(AHKCode, 1, -3)
    KeysDown.Delete(AHKCode)
    global VfioCredentials
    PrintLn("keyup " Code)
}

; key bindings
;_____________
SC03B::
    Key(A_ThisHotkey, 67)
    KeyUp(A_ThisHotkey, 67)
    PrintLn("quit")
    ExitApp

AppsKey::
    String := EscapeText(Clipboard)
    PrintLn("clipboard_copy " String)
    Return

; F1 - F12
;SC03B::Key(A_ThisHotkey, 67)
;SC03B Up::KeyUp(A_ThisHotkey, 67)
SC03C::Key(A_ThisHotkey, 68)
SC03C Up::KeyUp(A_ThisHotkey, 68)
SC03D::Key(A_ThisHotkey, 69)
SC03D Up::KeyUp(A_ThisHotkey, 69)
~SC03E::Key(A_ThisHotkey, 70)
~SC03E Up::KeyUp(A_ThisHotkey, 70)
SC03F::Key(A_ThisHotkey, 71)
SC03F Up::KeyUp(A_ThisHotkey, 71)
SC040::Key(A_ThisHotkey, 72)
SC040 Up::KeyUp(A_ThisHotkey, 72)
SC041::Key(A_ThisHotkey, 73)
SC041 Up::KeyUp(A_ThisHotkey, 73)
SC042::Key(A_ThisHotkey, 74)
SC042 Up::KeyUp(A_ThisHotkey, 74)
SC043::Key(A_ThisHotkey, 75)
SC043 Up::KeyUp(A_ThisHotkey, 75)
SC044::Key(A_ThisHotkey, 76)
SC044 Up::KeyUp(A_ThisHotkey, 76)
SC057::Key(A_ThisHotkey, 95)
SC057 Up::KeyUp(A_ThisHotkey, 95)
SC058::Key(A_ThisHotkey, 96)
SC058 Up::KeyUp(A_ThisHotkey, 96)
; ` --> =
SC029::Key(A_ThisHotkey, 49)
SC029 Up::KeyUp(A_ThisHotkey, 49)
SC002::Key(A_ThisHotkey, 10)
SC002 Up::KeyUp(A_ThisHotkey, 10)
SC003::Key(A_ThisHotkey, 11)
SC003 Up::KeyUp(A_ThisHotkey, 11)
SC004::Key(A_ThisHotkey, 12)
SC004 Up::KeyUp(A_ThisHotkey, 12)
SC005::Key(A_ThisHotkey, 13)
SC005 Up::KeyUp(A_ThisHotkey, 13)
SC006::Key(A_ThisHotkey, 14)
SC006 Up::KeyUp(A_ThisHotkey, 14)
SC007::Key(A_ThisHotkey, 15)
SC007 Up::KeyUp(A_ThisHotkey, 15)
SC008::Key(A_ThisHotkey, 16)
SC008 Up::KeyUp(A_ThisHotkey, 16)
SC009::Key(A_ThisHotkey, 17)
SC009 Up::KeyUp(A_ThisHotkey, 17)
SC00A::Key(A_ThisHotkey, 18)
SC00A Up::KeyUp(A_ThisHotkey, 18)
SC00B::Key(A_ThisHotkey, 19)
SC00B Up::KeyUp(A_ThisHotkey, 19)
SC00C::Key(A_ThisHotkey, 20)
SC00C Up::KeyUp(A_ThisHotkey, 20)
SC00D::Key(A_ThisHotkey, 21)
SC00D Up::KeyUp(A_ThisHotkey, 21)
; q --> ]
SC010::Key(A_ThisHotkey, 24)
SC010 Up::KeyUp(A_ThisHotkey, 24)
SC011::Key(A_ThisHotkey, 25)
SC011 Up::KeyUp(A_ThisHotkey, 25)
SC012::Key(A_ThisHotkey, 26)
SC012 Up::KeyUp(A_ThisHotkey, 26)
SC013::Key(A_ThisHotkey, 27)
SC013 Up::KeyUp(A_ThisHotkey, 27)
SC014::Key(A_ThisHotkey, 28)
SC014 Up::KeyUp(A_ThisHotkey, 28)
SC015::Key(A_ThisHotkey, 29)
SC015 Up::KeyUp(A_ThisHotkey, 29)
SC016::Key(A_ThisHotkey, 30)
SC016 Up::KeyUp(A_ThisHotkey, 30)
SC017::Key(A_ThisHotkey, 31)
SC017 Up::KeyUp(A_ThisHotkey, 31)
SC018::Key(A_ThisHotkey, 32)
SC018 Up::KeyUp(A_ThisHotkey, 32)
SC019::Key(A_ThisHotkey, 33)
SC019 Up::KeyUp(A_ThisHotkey, 33)
SC01A::Key(A_ThisHotkey, 34)
SC01A Up::KeyUp(A_ThisHotkey, 34)
SC01B::Key(A_ThisHotkey, 35)
SC01B Up::KeyUp(A_ThisHotkey, 35)
; a --> \
SC01E::Key(A_ThisHotkey, 38)
SC01E Up::KeyUp(A_ThisHotkey, 38)
SC01F::Key(A_ThisHotkey, 39)
SC01F Up::KeyUp(A_ThisHotkey, 39)
SC020::Key(A_ThisHotkey, 40)
SC020 Up::KeyUp(A_ThisHotkey, 40)
SC021::Key(A_ThisHotkey, 41)
SC021 Up::KeyUp(A_ThisHotkey, 41)
SC022::Key(A_ThisHotkey, 42)
SC022 Up::KeyUp(A_ThisHotkey, 42)
SC023::Key(A_ThisHotkey, 43)
SC023 Up::KeyUp(A_ThisHotkey, 43)
SC024::Key(A_ThisHotkey, 44)
SC024 Up::KeyUp(A_ThisHotkey, 44)
SC025::Key(A_ThisHotkey, 45)
SC025 Up::KeyUp(A_ThisHotkey, 45)
SC026::Key(A_ThisHotkey, 46)
SC026 Up::KeyUp(A_ThisHotkey, 46)
SC027::Key(A_ThisHotkey, 47)
SC027 Up::KeyUp(A_ThisHotkey, 47)
SC028::Key(A_ThisHotkey, 48)
SC028 Up::KeyUp(A_ThisHotkey, 48)
SC02B::Key(A_ThisHotkey, 51)
SC02B Up::KeyUp(A_ThisHotkey, 51)
; z --> <
SC02C::Key(A_ThisHotkey, 52)
SC02C Up::KeyUp(A_ThisHotkey, 52)
SC02D::Key(A_ThisHotkey, 53)
SC02D Up::KeyUp(A_ThisHotkey, 53)
SC02E::Key(A_ThisHotkey, 54)
SC02E Up::KeyUp(A_ThisHotkey, 54)
SC02F::Key(A_ThisHotkey, 55)
SC02F Up::KeyUp(A_ThisHotkey, 55)
SC030::Key(A_ThisHotkey, 56)
SC030 Up::KeyUp(A_ThisHotkey, 56)
SC031::Key(A_ThisHotkey, 57)
SC031 Up::KeyUp(A_ThisHotkey, 57)
SC032::Key(A_ThisHotkey, 58)
SC032 Up::KeyUp(A_ThisHotkey, 58)
SC033::Key(A_ThisHotkey, 59)
SC033 Up::KeyUp(A_ThisHotkey, 59)
SC034::Key(A_ThisHotkey, 60)
SC034 Up::KeyUp(A_ThisHotkey, 60)
SC035::Key(A_ThisHotkey, 61)
SC035 Up::KeyUp(A_ThisHotkey, 61)
SC073::Key(A_ThisHotkey, 94)
SC073 Up::KeyUp(A_ThisHotkey, 94)
; rest
SC001::Key(A_ThisHotkey, 9) ; Esc
SC001 Up::KeyUp(A_ThisHotkey, 9)
SC00E::Key(A_ThisHotkey, 22) ; BS
SC00E Up::KeyUp(A_ThisHotkey, 22)
SC01C::Key(A_ThisHotkey, 36) ; Enter
SC01C Up::KeyUp(A_ThisHotkey, 36)
SC00F::Key(A_ThisHotkey, 23) ; Tab
SC00F Up::KeyUp(A_ThisHotkey, 23)
CapsLock::Key(A_ThisHotkey, 66)
CapsLock Up::KeyUp(A_ThisHotkey, 66)
LShift::Key(A_ThisHotkey, 50)
LShift Up::KeyUp(A_ThisHotkey, 50)
RShift::Key(A_ThisHotkey, 62)
RShift Up::KeyUp(A_ThisHotkey, 62)
LCtrl::Key(A_ThisHotkey, 37)
LCtrl Up::KeyUp(A_ThisHotkey, 37)
RCtrl::Key(A_ThisHotkey, 105)
RCtrl Up::KeyUp(A_ThisHotkey, 105)
LWin::Key(A_ThisHotkey, 133)
LWin Up::KeyUp(A_ThisHotkey, 133)
LAlt::Key(A_ThisHotkey, 64)
LAlt Up::KeyUp(A_ThisHotkey, 64)
SC07B::Key(A_ThisHotkey, 102) ; muhenkan
SC07B Up::KeyUp(A_ThisHotkey, 102)
SC039::Key(A_ThisHotkey, 65) ; space
SC039 Up::KeyUp(A_ThisHotkey, 65)
SC079::Key(A_ThisHotkey, 100) ; henkan
SC079 Up::KeyUp(A_ThisHotkey, 100)
SC070::Key(A_ThisHotkey, 101) ; hira/kata (BS)
SC070 Up::Keyup(A_ThisHotkey, 101)
;AppsKey::Return
; nav
PrintScreen::Key(A_ThisHotkey, 107)
PrintScreen Up::KeyUp(A_ThisHotkey, 107)
ScrollLock::Key(A_ThisHotkey, 78)
ScrollLock Up::KeyUp(A_ThisHotkey, 78)
Pause::Key(A_ThisHotkey, 127)
Pause Up::KeyUp(A_ThisHotkey, 127)
;;;
Insert::Key(A_ThisHotkey, 118)
Insert Up::KeyUp(A_ThisHotkey, 118)
Delete::Key("SC053", 119)
Delete Up::KeyUp("SC053 Up", 119)
Home::Key(A_ThisHotkey, 110)
Home Up::KeyUp(A_ThisHotkey, 110)
End::Key(A_ThisHotkey, 115)
End Up::KeyUp(A_ThisHotkey, 115)
PgUp::Key(A_ThisHotkey, 112)
PgUp Up::KeyUp(A_ThisHotkey, 112)
PgDn::Key(A_ThisHotkey, 117)
PgDn Up::KeyUp(A_ThisHotkey, 117)
;;;
Up::Key(A_ThisHotkey, 111)
Up Up::KeyUp(A_ThisHotkey, 111)
Down::Key(A_ThisHotkey, 116)
Down Up::KeyUp(A_ThisHotkey, 116)
Left::Key(A_ThisHotkey, 113)
Left Up::KeyUp(A_ThisHotkey, 113)
Right::Key(A_ThisHotkey, 114)
Right Up::KeyUp(A_ThisHotkey, 114)
; disable mouse buttons
LButton::
MButton::
RButton::
WheelDown::
WheelUp::
WheelLeft::
WheelRight::
XButton1::
XButton2::
Return
