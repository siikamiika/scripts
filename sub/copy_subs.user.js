// ==UserScript==
// @name         copy subs
// @namespace    miika.es
// @version      0.1
// @description  copy subs
// @author       siikamiika
// @match        http://localhost:9874/*
// ==/UserScript==

var text_input = document.getElementById('text-input');
var address = 'ws://localhost:9873/'
var ws = new WebSocket(address);
ws.onmessage = function (text) {
    text_input.value = text.data;
    //text_input.oninput();
    angular.element(text_input).triggerHandler('change');
}
