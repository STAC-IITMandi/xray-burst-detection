
var finput = document.getElementById('formFile');
var formatDiv = document.getElementById('detectedFileFormat');
var formatSpan = document.getElementById('fileFormatLabel');
var formatHint = document.getElementById('fileTypeHint');
const _maxFileMegaBytes = 200;
var contentDiv = document.getElementById('uploadContainer');
var dddisp = document.getElementById('dragDropDisplay');
var _dragDropCount = 0;


function allText(string) {
    for (let i=0; i<string.length; i++) {
        let cc = string.codePointAt(i);
        if (! (cc >= 0x20 && cc < 0x7f ||
               cc >= 0x08 && cc < 0x0e ||
               cc === 0 || cc === 0x1b))
        return false;
    }
    return true;
}

function inspectFile(string) {
    if (string.slice(0,30) === 'SIMPLE  =                    T') {
        formatSpan.innerHTML = `<span class="badge bg-success">FITS</span>`;
        formatHint.value = "fits";
    } else if (string.slice(0,4) === '\x50\x4B\x03\x04') {
        formatSpan.innerHTML = `<span class="badge bg-success">XLSX</span>`;
        formatHint.value = "xlsx";
    } else if (allText(string.slice(0,500))) {
        formatSpan.innerHTML = `<span class="badge bg-warning">ASCII Text</span>`;
        formatHint.value = "txt";
    } else {
        formatSpan.innerHTML = `<span class="badge bg-danger">Unrecognised</span>`;
        formatHint.value = "";
    }
}

function fileAddedHandler(loadevent) {
    if (finput.files.length > 0) {
        let file = finput.files[0];
        if (file.size > _maxFileMegaBytes*1024*1024) {
            finput.value = '';
            alert(`This file is too large ! Please only try uploading files less than ${_maxFileMegaBytes} MB`)
            formatDiv.classList.add('d-none');
        } else {
            var reader = new FileReader();
            reader.onload = () => { inspectFile(reader.result); }
            reader.readAsBinaryString(file);
            formatDiv.classList.remove('d-none');
        }
    } else {
        formatDiv.classList.add('d-none');
    }
}


finput.addEventListener('change', fileAddedHandler);

contentDiv.ondragover = (event) => {
    event.preventDefault();
}
contentDiv.ondragenter = function(event) {
    event.preventDefault();
    _dragDropCount++;
    dddisp.classList.remove('d-none');
}
contentDiv.ondragleave = function(event) {
    _dragDropCount--;
    if (_dragDropCount <= 0)
        dddisp.classList.add('d-none');
}
contentDiv.ondrop = function(event) {
    console.log('d', event.dataTransfer.files);
    finput.files = event.dataTransfer.files;
    event.preventDefault();
    _dragDropCount = 0;
    dddisp.classList.add('d-none');
    fileAddedHandler();
}
