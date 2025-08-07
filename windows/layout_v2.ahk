#Requires AutoHotkey v2.0
#Warn
#SingleInstance Force

global isRightAlt := false

*RAlt:: {
    global isRightAlt := true
    return
}

*RAlt Up:: {
    global isRightAlt := false
    return
}

+CapsLock::CapsLock
CapsLock::Esc

*a:: {
    if isRightAlt {
        if GetKeyState("Shift", "P") ^ GetKeyState("CapsLock", "T") {
            Send "{Blind}Ä"
        } else {
            Send "{Blind}ä"
        }
    } else {
        Send "{Blind}a"
    }
}

*o:: {
    if isRightAlt {
        if GetKeyState("Shift", "P") ^ GetKeyState("CapsLock", "T") {
            Send "{Blind}Ö"
        } else {
            Send "{Blind}ö"
        }
    } else {
        Send "{Blind}o"
    }
}

*h:: Send isRightAlt ? "{Blind}{Left}"  : "{Blind}h"
*j:: Send isRightAlt ? "{Blind}{Down}"  : "{Blind}j"
*k:: Send isRightAlt ? "{Blind}{Up}"    : "{Blind}k"
*l:: Send isRightAlt ? "{Blind}{Right}" : "{Blind}l"

*p::     Send isRightAlt ? "{Blind}{Home}" : "{Blind}p"
*SC027:: Send isRightAlt ? "{Blind}{End}"  : "{Blind}{SC027}"

*[:: Send isRightAlt ? "{Blind}{PgUp}" : "{Blind}["
*':: Send isRightAlt ? "{Blind}{PgDn}" : "{Blind}'"

*u:: Send isRightAlt ? "{Blind}{Delete}" : "{Blind}u"
*i:: Send isRightAlt ? "{Blind}{Insert}" : "{Blind}i"
