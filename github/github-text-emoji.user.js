// ==UserScript==
// @name         Github Text Emoji
// @namespace    http://miika.es/
// @version      0.1
// @description  Show emoji as text on Github
// @author       siikamiika
// @match        https://github.com/*
// @grant        none
// ==/UserScript==

function parseEmoji(url) {
    // https://github.githubassets.com/images/icons/emoji/unicode/1f1eb-1f1ee.png
    const match = url.match(/emoji\/unicode\/([0-9a-f\-]+)\.png/);
    if (match && match[1]) {
        return String.fromCodePoint(...match[1].split('-').map(hex => parseInt(hex, 16)));
    }
}

function convertEmojiToTextOnPage() {
    document.querySelectorAll('g-emoji').forEach((emojiElement) => {
        const emojiText = parseEmoji(emojiElement.getAttribute('fallback-src'));
        if (emojiText) {
            emojiElement.parentNode.replaceChild(
                document.createTextNode(emojiText),
                emojiElement
            );
        }
    });
}

window.setInterval(_ => convertEmojiToTextOnPage(), 500);
