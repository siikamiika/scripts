// ==UserScript==
// @name        New script - google.com
// @namespace   s
// @match       https://translate.google.com/
// @grant       none
// @version     1.0
// @author      -
// @description 2022/1/17 0:51:26
// ==/UserScript==

(() => {
    let state = 1;
    window.addEventListener('keydown', (e) => {
        if (e.key === ' ' && e.altKey) {
            if (state === 1) {
                document.querySelector('li.ita-kd-menuitem:nth-child(1)').click()
                state = 2;
            } else if (state === 2) {
                document.querySelector('li.ita-kd-menuitem:nth-child(2)').click()
                state = 1;
            }
        } else if (e.key === 'r' && e.altKey) {
            document.querySelector('[data-enable-toggle-playback-speed="true"]').querySelectorAll('button').forEach((b) => b.click())
        }
    });
})();
