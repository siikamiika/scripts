#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

SC07B & ':: Send {ä}
SC079 & ':: Send {Ä}

SC07B & `;:: Send {ö}
SC079 & `;:: Send {Ö}

SC07B & [:: Send {å}
SC079 & [:: Send {Å}

+CapsLock::CapsLock
Capslock::Esc