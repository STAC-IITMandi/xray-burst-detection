
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

@app.route('/')
def landing_page():
    return render_template('landing.html')


@app.route('/analysis', methods=['GET','POST'])
def analysis_page():

    if request.method == 'POST':

        id = str(uuid.uuid1())
        f = request.files['formFile']
        d = os.path.join(PATHBASE, 'uploads', id)
        if not os.path.isdir(d):
            os.mkdir(d)
        f.save(os.path.join(d,'raw'))
        
        logger.info(f"Created file {id}")
        fileparsers.DATA.add_row(
            [id,datetime.datetime.now(),f.filename,'PROCESSING','']
        )
        # t = threading.Thread(target=fileparsers.analyse,
        #                      args=(id, request.form))
        # t.start()
        fileparsers.analyse(id, request.form)

        return redirect(f'/analysis?upload={id}', 303)

    else :
        if 'upload' in request.args :
            for row in fileparsers.DATA :
                if row['id'] == request.args['upload'] :
                    return render_template('analysis.html', id=row['id'], filename=row['filename'])
            return render_template('error.html', code=404, error='Not Found'), 404
        else :
            return render_template('error.html', code=400, error='Bad Request'), 400


@app.route('/data/<s>/<id>')
def data_server(s, id):
    if os.path.isdir(os.path.join(PATHBASE, 'uploads', id)):
        if s == 'timeseries' :
            fp = os.path.join(PATHBASE, 'uploads', id, 'timeseries.json')
            if os.path.isfile(fp):
                return send_file(fp, mimetype='application/json')
            else :
                return {'status':'UNAVAILABLE',}
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



def cleaner():
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
    _debug = os.environ.get('DEBUG','').lower() == 'true'
    _cleanerprocess = threading.Thread(target=cleaner)
    _cleanerprocess.start()
    app.run(host='0.0.0.0', port=5000, debug=_debug)
