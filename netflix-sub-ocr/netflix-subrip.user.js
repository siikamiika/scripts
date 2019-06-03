// ==UserScript==
// @name         netflix-subrip
// @version      0.1
// @description  netflix-subrip
// @author       siikamiika
// @match        https://www.netflix.com/watch/*
// @grant        none
// ==/UserScript==

let querySelector = document.querySelector.bind(document);

function toDataURL(url, cb) {
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
        let f = new FileReader();
        f.onloadend = () => {
            cb(f.result);
        }
        f.readAsDataURL(xhr.response);
    };
    xhr.open('GET', url);
    xhr.responseType = 'blob';
    xhr.send();
}

window.setTimeout(() => {
    let subtitles = querySelector('.image-based-timed-text svg');
    new MutationObserver(function(mutations) {
        let img = mutations[0].target.firstChild;
        toDataURL(img.href.baseVal, function(dataUrl) {
            console.log(dataUrl);
            let img = document.createElement('img');
            img.src = 'http://localhost:9873/fake_image?image_data='+encodeURIComponent(dataUrl);
        });
    }).observe(
        subtitles,
        {childList: true}
    );
}, 5000);
