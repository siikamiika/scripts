#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance force

; SC07B == 無変換, SC079 == 変換

; TOP ROW

q::Send, 。
SC07B & q::Send, ぁ
SC079 & q::Send, 。

w::Send, か
SC07B & w::Send, え
SC079 & w::Send, が

e::Send, た
SC07B & e::Send, り
SC079 & e::Send, だ

r::Send, こ
SC07B & r::Send, ゃ
SC079 & r::Send, ご

t::Send, さ
SC07B & t::Send, れ
SC079 & t::Send, ざ

;;;;;;;;;;;;;;;;;;

y::Send, ら
SC07B & y::Send, ぱ
SC079 & y::Send, よ

u::Send, ち
SC07B & u::Send, ぢ
SC079 & u::Send, に

i::Send, く
SC07B & i::Send, ぐ
SC079 & i::Send, る

o::Send, つ
SC07B & o::Send, づ
SC079 & o::Send, ま

p::Send, 、
+p::SendRaw, ；
SC07B & p::Send, ぴ
SC079 & p::Send, ぇ

; MIDDLE ROW

a::Send, う
SC07B & a::Send, を
SC079 & a::Send, ゔ

s::Send, し
SC07B & s::Send, あ
SC079 & s::Send, じ

d::Send, て
SC07B & d::Send, な
SC079 & d::Send, で

f::Send, け
SC07B & f::Send, ゅ
SC079 & f::Send, げ

g::Send, せ
SC07B & g::Send, も
SC079 & g::Send, ぜ

;;;;;;;;;;;;;;;;;;

h::Send, は
+h::Send, ぱ
SC07B & h::Send, ば
SC079 & h::Send, み

j::Send, と
SC07B & j::Send, ど
SC079 & j::Send, お

k::Send, き
SC07B & k::Send, ぎ
SC079 & k::Send, の

l::Send, い
SC07B & l::Send, ぽ
SC079 & l::Send, ょ

`;::Send, ん
$+`;::Send, :
SC07B & `;::Send, ん
SC079 & `;::Send, っ

; BOTTOM ROW

SC07B & z::Send, ぅ
SC079 & z::Send, ・

x::Send, ひ
+x::Send, ぴ
SC07B & x::Send, ー
SC079 & x::Send, び

c::Send, す
SC07B & c::Send, ろ
SC079 & c::Send, ず

v::Send, ふ
+v::Send, ぷ
SC07B & v::Send, や
SC079 & v::Send, ぶ

b::Send, へ
+b::Send, ぺ
SC07B & b::Send, ぃ
SC079 & b::Send, べ

;;;;;;;;;;;;;;;;;;

n::Send, め
SC07B & n::Send, ぷ
SC079 & n::Send, ぬ

m::Send, そ
SC07B & m::Send, ぞ
SC079 & m::Send, ゆ

,::Send, ね
SC07B & ,::Send, ぺ
SC079 & ,::Send, む

.::Send, ほ
SC07B & .::Send, ぼ
SC079 & .::Send, わ

SC079 & /::Send, ぉ


; close when other layouts are activated
~!+1::ExitApp
~!+3::ExitApp
