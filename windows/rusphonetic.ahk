#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance force

Key(upper, lower, original) {
    if GetKeyState("Ctrl") or GetKeyState("Alt") or GetKeyState("LWin") or GetKeyState("RWin")
        Send, {Blind}{%original%}
    else if GetKeyState("CapsLock", "T")
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

*`::Key("Ё", "ё", "`")
*=::Key("Ъ", "ъ", "=")
*q::Key("Я", "я", "q")
*w::Key("Ш", "ш", "w")
*e::Key("Е", "е", "e")
*r::Key("Р", "р", "r")
*t::Key("Т", "т", "t")
*y::Key("Ы", "ы", "y")
*u::Key("У", "у", "u")
*i::Key("И", "и", "i")
*o::Key("О", "о", "o")
*p::Key("П", "п", "p")
*[::Key("Ю", "ю", "[")
*]::Key("Щ", "щ", "]")
*a::Key("А", "а", "a")
*s::Key("С", "с", "s")
*d::Key("Д", "д", "d")
*f::Key("Ф", "ф", "f")
*g::Key("Г", "г", "g")
*h::Key("Ч", "ч", "h")
*j::Key("Й", "й", "j")
*k::Key("К", "к", "k")
*l::Key("Л", "л", "l")
*`;::Key("Ь", "ь", ";")
*'::key("Ж", "ж", "'")
*z::Key("З", "з", "z")
*x::Key("Х", "х", "x")
*c::Key("Ц", "ц", "c")
*v::Key("В", "в", "v")
*b::Key("Б", "б", "b")
*n::Key("Н", "н", "n")
*m::Key("М", "м", "m")


; close when other layouts are activated
~!+1::ExitApp
~!+2::ExitApp
