// ==UserScript==
// @name         Google Without Consent
// @namespace    siikamiika
// @version      0.1
// @description  Google Without Consent
// @author       siikamiika
// @match        https://www.google.com/search*
// @grant        none
// ==/UserScript==

(() => {
    if (!document.querySelector('iframe[src*="consent"]')) { return; }

    const transformLinks = (res) => Array.from(res.querySelectorAll('a'))
        .filter((l) => l.getAttribute('onmousedown')?.startsWith('return'))
        .map((l) => ({href: l.href, textContent: l.href}));
    const transformTitle = (res) => ({textContent: res.querySelector('h3')?.textContent});
    const transformBody = (res) => ({
        textContent: Array.from(res.querySelectorAll('span'))
            .sort((a, b) => a.textContent.length < b.textContent.length)
            ?.[0]
            .textContent
    });
    const searchResults = Array.from(document.querySelector('#search').querySelectorAll('.g'))
        .map((res) => ({
            links: transformLinks(res),
            title: transformTitle(res),
            body: transformBody(res),
        }));

    const navigation = Array.from(document.querySelector('#foot').querySelector('table tr').querySelectorAll('td'))
        .map((d) => ({href: d.querySelector('a')?.href, textContent: d.textContent}));

    const getUrlVariant = (url, variant) => {
        const urlObj = new URL(url);
        switch (variant) {
            case 'search':
                urlObj.searchParams.delete('tbm');
                break;
            case 'image':
                urlObj.searchParams.set('tbm', 'isch');
                break;
            case 'video':
                urlObj.searchParams.set('tbm', 'vid');
                break;
            default:
                throw new Error(`Invalid variant: ${variant}`);
        }
        return urlObj.toString();
    };

    const searchTypes = document.createElement('ul');
    for (const searchVariant of ['search', 'image', 'video']) {
        const row = document.createElement('li');
        row.appendChild(Object.assign(
            document.createElement('a'),
            {href: getUrlVariant(document.location.href, searchVariant), textContent: searchVariant}
        ));
        searchTypes.appendChild(row);
    }

    const rows = document.createElement('ul');
    for (const result of searchResults) {
        const row = document.createElement('li');
        row.appendChild(Object.assign(
            document.createElement('h3'),
            result.title
        ));
        row.appendChild(Object.assign(
            document.createElement('p'),
            result.body
        ));
        const subRows = document.createElement('ul');
        for (const link of result.links) {
            const subRow = document.createElement('li');
            subRow.appendChild(Object.assign(
                document.createElement('a'),
                link
            ));
            subRows.appendChild(subRow);
        }
        row.appendChild(subRows);
        rows.appendChild(row);
    }

    const navLinks = document.createElement('ul');
    for (const navLink of navigation) {
        navLinkRow = document.createElement('li');
        navLinkRow.appendChild(Object.assign(
            navLink.href ? document.createElement('a') : document.createElement('span'),
            navLink
        ));
        navLinks.appendChild(navLinkRow);
    }

    document.documentElement.innerHTML = searchTypes.outerHTML + rows.outerHTML + navLinks.outerHTML;
})();
