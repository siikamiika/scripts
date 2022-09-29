// ==UserScript==
// @name        YouTube Longs
// @namespace   siikamiika
// @match       https://www.youtube.com/shorts/*
// @grant       none
// @version     1.0
// @author      siikamiika
// @description Redirect Shorts to regular video page
// ==/UserScript==

(() => {
    const parts = window.location.href.match(/(https:\/\/www.youtube.com\/)shorts\/([^\/\?]+)/);
    window.location.href = `${parts[1]}watch?v=${parts[2]}`;
})();
