"""
Solar X-Ray Burst Identifier
===============================
Developed by the team at IIT Mandi
Inter-IIT Tech meet 10.0 (March 2022) - ISRO's Mid Prep problem
-------------------------------
https://github.com/STAC-IITMandi/xray-burst-detection
License & Authors : See the `LICENSE` file and Github repository
"""

"""
This file is the entry point of the web server.
"""

from flask import Flask, render_template, request, redirect, send_file
from dotenv import load_dotenv

import fileparsers

import os
import shutil
import datetime
import threading
import logging
import uuid
import time


load_dotenv()
PATHBASE = os.path.abspath(os.path.dirname(__file__))

app = Flask('XrayIDapp')


logger = logging.getLogger('webserver')
logging.basicConfig(level=logging.INFO,
    format='%(name)-10s %(levelname)-8s [%(asctime)s] %(message)s',
)

# ***************************************
# BEGIN server route definitions
# ***************************************


@app.route('/')
def landing_page():
    """Home page. User can upload files from here"""
    return render_template('landing.html')

@app.route('/guide')
def guide_page():
    """User Guide. Info on working of the app"""
    return render_template('guide.html')


@app.route('/analysis', methods=['GET','POST'])
def analysis_page():
    """
    Page where the visualisation is shown.

    Uploaded files are POSTed to this url, then a UUID is generated for them and 
    they are stored on the filesystem, then the `fileparsers` module takes over
    processing of the data.

    Meanwhile, the user is redirected to the page with the visualisation,
    by GETting this url along with the uuid, which is used to uniquely identify
    this upload in all places from now on.
    """
    if request.method == 'POST':

        id = str(uuid.uuid1())
        f = request.files['formFile']
        d = os.path.join(PATHBASE, 'uploads', id)
        if not os.path.isdir(d):
            os.mkdir(d)
        f.save(os.path.join(d,'raw'))
        
        logger.info(f"Created file {id}")
        fileparsers.DATA.add_row(
            [id,datetime.datetime.now(),f.filename,'PROCESSING','',False]
        )
        t = threading.Thread(target=fileparsers.analyse,
                             args=(id, request.form))
        t.start()
        # fileparsers.analyse(id, request.form)

        return redirect(f'/analysis?upload={id}', 303)

    else :
        if 'upload' in request.args :
            for row in fileparsers.DATA :
                if row['id'] == request.args['upload'] :
                    return render_template('analysis.html', id=row['id'], filename=row['filename'])
            return render_template('error.html', code=404, error='Not Found'), 404
        else :
            return render_template('error.html', code=400, error='Bad Request'), 400


@app.route('/status/<id>')
def status_check(id):
    """Return JSON with info about whether the uploaded file has been parsed successfully."""
    if os.path.isdir(os.path.join(PATHBASE, 'uploads', id)):
        for row in fileparsers.DATA:
            if row['id']==id :
                stat, msg, err = row['status'], row['message'], bool(row['error_included'])
                break
        return {'status':stat, 'message':msg, 'error_included':err}
    else :
        return '', 404


@app.route('/data/<s>/<id>')
def data_server(s, id):
    """
    Return the parsed data files (stored on filesystem) for the timeseries,
    and also its detected bursts / statistical model results, for an upload.

    Timeseries is served only for graph plotting, in CSV format required by the library.
    Result data is served in JSON (for the graph), and all other formats defined in
    `fileparsers.write`, for the user to download.
    """
    if os.path.isdir(os.path.join(PATHBASE, 'uploads', id)):

        if s == 'timeseries' :
            fp = os.path.join(PATHBASE, 'uploads', id, 'timeseries.csv')
            if os.path.isfile(fp):
                return send_file(fp, mimetype='text/csv')
            else :
                return '', 404
    
        elif s == 'result' :
            request_format = request.args.get('format','json')
            for fmt, mimetype in zip(('csv','xlsx','fits'),
                ('text/csv','application/vnd.ms-excel','application/fits')):
                fp = os.path.join(PATHBASE, 'uploads', id, f'result.{fmt}')
                if request_format==fmt :
                    if os.path.isfile(fp) :
                        return send_file(fp, mimetype=mimetype)
                    else :
                        return '', 404
            fp = os.path.join(PATHBASE, 'uploads', id, 'result.json')
            if request_format != 'json':
                return '', 404
            if os.path.isfile(fp) :
                return send_file(fp, mimetype='application/json')
            else :
                return {'status':'UNAVAILABLE',}
        else :
            return '', 400
    else :
        return '', 404


# End of server route definitions



def cleaner():
    """
    This function runs in a separate thread, with the sole purpose of removing
    uploaded files & associated data whenever their storage duration has expired;
    and their entry from the server database (`fileparsers.DATA`).
    Any existing files present when the server starts are also cleaned.
    """
    global app, PATHBASE
    logger = logging.getLogger('fileclean')
    logger.info('Cleaning up old files')
    x=[]
    for d in os.scandir(os.path.join(PATHBASE, 'uploads')):
        if os.path.isdir(d):
            try :
                shutil.rmtree(d, ignore_errors=True)
                x.append(d)
            except :
                continue
    logger.info("Removed"+str(x))
    while True :
        x = []
        for i, (id, t) in enumerate(zip(fileparsers.DATA['id'], fileparsers.DATA['upload_time'])) :
            if datetime.datetime.now() > t + fileparsers.UPLOAD_LIFETIME :
                try :
                    shutil.rmtree(os.path.join(PATHBASE, 'uploads', id), ignore_errors=True)
                    x.append(i)
                    logger.info(f"Deleted {id}")
                except :
                    logger.exception(f"Couldn't delete {id}")
        fileparsers.DATA.remove_rows(x)
        time.sleep(60 * 5)



if __name__ == '__main__':
    print("""___________________________________________________

Server starting...
Please visit http://localhost:5115/ in your browser
___________________________________________________
""")
    _debug = os.environ.get('DEBUG','').lower() == 'true'
    _cleanerprocess = threading.Thread(target=cleaner)
    _cleanerprocess.start()
    app.run(host='0.0.0.0', port=5115, debug=_debug)
