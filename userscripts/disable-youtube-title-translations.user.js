// ==UserScript==
// @name         disable-youtube-title-translations
// @namespace    http://miika.es/
// @version      0.1
// @description  disable youtube title translations
// @author       siikamiika
// @match        http*://www.youtube.com/*
// @grant        none
// ==/UserScript==

// use `document` in other scopes
let querySelector = document.querySelector.bind(document);

// initialize variables
let originalTitle,
    titleElement;

// poll original title from page title each second
let intervalId = setInterval(function() {
    originalTitle = document.title.slice(0, -10);
    titleElement = querySelector('#container .title');
    if (titleElement && originalTitle) {
        titleElement.innerText = originalTitle;
    }
}, 1000);
