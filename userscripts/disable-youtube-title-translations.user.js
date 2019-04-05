// ==UserScript==
// @name         disable-youtube-title-translations
// @version      0.1
// @description  disable youtube title translations
// @author       siikamiika
// @match        https://www.youtube.com/*
// @grant        none
// ==/UserScript==

// use `document` in other scopes
let querySelector = document.querySelector.bind(document);

// initialize variables
let originalTitle,
    titleElement;

// observe changes to page title, updating the video title accordingly
let title = querySelector('title');
new MutationObserver(function(mutations) {
    console.log(mutations[0].target.text);
    // strip ` - Youtube`
    originalTitle = mutations[0].target.text.slice(0, -10);
    //  set video title to page title
    titleElement = querySelector('#container .title');
    titleElement.innerText = originalTitle;
}).observe(
    title,
    {childList: true}
);
