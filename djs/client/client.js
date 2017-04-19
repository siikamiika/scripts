var XHR = function(type, path, data, onready, async) {
    if (!onready) {onready = function(){}}
    if (!(async === false)) {async = true};
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            onready(xhr.responseText);
        }
    }

    xhr.open(type, path, async);
    xhr.send(data);
}

var inputElement = document.getElementById('search-input');
var resultsElement = document.getElementById('search-results');

inputElement.oninput = function(e) {
    XHR('GET', '/dictionary?query='+encodeURIComponent(this.value), null, function(results) {
        resultsElement.innerHTML = JSON.parse(results).map(processResult).join('<hr>');
    });
}

function processResult(result) {
    var output = [];
    output.push('<div>');
    output.push('<h1>');
    output.push(result[0]);
    output.push('【'+result[1]+'】');
    output.push('</h1>');
    output.push(result[6]);
    output.push('</div>');
    return output.join('');
}

