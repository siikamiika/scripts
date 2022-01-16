// not actually userscript (yet?)
// just copy paste to translate.google.com

(() => {
    let state = 1;
    window.addEventListener('keydown', (e) => {
        if (e.key === 'HiraganaKatakana') {
            if (state === 1) {
                document.querySelector('li.ita-kd-menuitem:nth-child(1)').click()
                state = 2;
            } else if (state === 2) {
                document.querySelector('li.ita-kd-menuitem:nth-child(2)').click()
                state = 1;
            }
        }
    });
})();
