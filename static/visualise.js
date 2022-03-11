
function ajax(method, url, ok_handler, err_handler=undefined) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(event) {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200)
                ok_handler(xhr.responseText);
            else if (err_handler != undefined)
                err_handler(xhr.response, xhr.status);
        }
    }
    xhr.open(method, url);
    xhr.send();
}

