
var _sdi = 0;
const backoffDelays = [0.1, 0.2, 0.4, 1, 2, 5];
var _ajaxdata_status, _ajaxdata_result;

function ajax(method, url, ok_handler, ok_args=undefined, retry_handler=undefined, err_handler=undefined) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(event) {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200 || xhr.status === 304) {
                checkStatus(xhr.responseText, ok_handler, ok_args, retry_handler);
            } else if (err_handler !== undefined) {
                err_handler(xhr.response, xhr.status);
            }
        }
    }
    xhr.open(method, url);
    xhr.send();
}

function load1() {
    ajax('GET', `/status/${_uploadID}`, load2, '_ajaxdata_status', load1);
}
function load2() {
    ajax('GET', `/data/result/${_uploadID}`, plotGraph, '_ajaxdata_result', load2);
}

function checkStatus(content, okfunc, locvar=undefined, retryfunc=undefined) {
    var c = JSON.parse(content);
    if (c.status === 'OK') {
        if (locvar !== undefined) window[locvar] = c;
        okfunc()
    } else if (c.status === 'ERROR') {
        showErrorDialog(c);
    } else if (retryfunc !== undefined) {
        if (_sdi < backoffDelays.length-1) _sdi++;
        setTimeout(retryfunc, backoffDelays[_sdi] * 1000)
    }
}

function showErrorDialog(statcontent) {
    var mde = document.getElementById('mainDivError')
    var mdl = document.getElementById('mainDivLoading')
    var errdesc = document.getElementById('errorReason')
    mde.classList.remove('d-none')
    mdl.classList.add('d-none')
    errdesc.innerText = statcontent.message;
}


function plotGraph() {
    let sh = screen.availHeight;
    let sw = screen.availWidth;
    var gc = document.getElementById('plotContainer')
    window._graphPlot = new Dygraph(
        gc, `/data/timeseries/${_uploadID}`,
        {
            legend:'always',
            title:'Light Curve',
            showRoller: true,
            rollPeriod: 1,
            errorBars: window._ajaxdata_status.error_included,
            sigma: 1.0,
            height : 500,
            width : sw * 0.7,
            showRangeSelector: true,
            ylabel: "Flux (in given units)",
            xlabel: "DateTime (UTC)",
            underlayCallback: boxPeaks
        }
    )
    var mdg = document.getElementById('mainDivGraph')
    var mdl = document.getElementById('mainDivLoading')
    mdg.classList.remove('d-none')
    mdl.classList.add('d-none')
    plotAnnotations();
}

function boxPeaks(canvas, area, g) {
    for (const b of window._ajaxdata_result.BURSTS) {
        let lt = (/\:/.test(String(b.start_time))) ? Date.parse(b.start_time) : b.start_time,
            rt = (/\:/.test(String(b.end_time))) ? Date.parse(b.end_time) : b.end_time;
        let l = g.toDomCoords(lt, 0)[0],
            r = g.toDomCoords(rt, 0)[0];
        canvas.fillStyle = "rgb(215, 255, 245)";
        canvas.fillRect(l, area.y, r-l, area.h);
    }
}

function plotAnnotations() {
    console.info('>>', window._ajaxdata_result, window._ajaxdata_status)
    var burstlist = window._ajaxdata_result.BURSTS;
    var th = document.querySelector('table#burstList thead tr')
    var tb = document.querySelector('table#burstList tbody')
    th.innerHTML = th.innerHTML.concat(`<th scope="col">#</th>`)
    for (const prop in burstlist[0]) {
        th.innerHTML = th.innerHTML.concat(
            `<th scope="col" class="text-capitalize">${prop.replaceAll('_',' ')}</th>`
        )
    }
    let i=1;
    var annos = [], table="";
    for (const b of burstlist) {
        table = table.concat(`<tr data-anno="${i}"><th scope="row">${i}</th>`)
        for (const p in b) {
            let bp;
            if ((p==='start_time'||p==='end_time'||p==='max_time') && /\:/.test(String(b[p])))
                bp = (new Date(b[p])).toLocaleString()
            else
                bp = b[p]
            table = table.concat(`<td>${bp}</td>`);
        }
        annos.push({
            series:'y',
            x: b.max_time,
            shortText: String(i),
            mouseOverHandler: annoTableAddHighlight,
            mouseOutHandler: annoTableRemHighlight,
            width: 24,
            height: 24
        });
        table = table.concat(`</tr>`)
        i++;
    }
    tb.innerHTML = table;
    console.log(annos)
    window._graphPlot.ready(() => {
        window._graphPlot.setAnnotations(annos);
    });
}

function annoTableAddHighlight(annotation, point, dygraph, event) {
    let tabr = document.querySelector(`tr[data-anno="${annotation.shortText}"]`);
    tabr.classList.add('highlight');
}
function annoTableRemHighlight(annotation, point, dygraph, event) {
    let tabr = document.querySelector(`tr[data-anno="${annotation.shortText}"]`);
    tabr.classList.remove('highlight');
}

// Fire the initial AJAX request to plot the graph
load1()
