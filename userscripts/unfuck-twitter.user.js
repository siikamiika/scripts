// ==UserScript==
// @name        unfuck twitter
// @namespace   siikamiika
// @match       https://twitter.com/*
// @grant       none
// @version     1.0
// @author      siikamiika
// @description 2022/5/15 13:59:29
// ==/UserScript==

(new MutationObserver((mutationsList, observer) => {
  for (const mutation of mutationsList) {
    const target = mutation.target;
    for (const prefix of [
      'See more Tweets from',
    ]) {
      if (target.textContent.startsWith(prefix)) {
        console.debug('unfucking loginwall', target);
        target.remove();
        document.documentElement.style.overflow = null;
        document.documentElement.style.overflowY = 'scroll';
        document.documentElement.style.marginRight = null;
        break;
      }
    }
  }
})).observe(document.body, {childList: true, subtree: true});
