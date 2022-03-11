
from flask import Flask, render_template, request, redirect
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

        id = str(uuid.uuid4())
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

        return render_template('base.html')



def cleaner():
    global app, PATHBASE
    logger = logging.getLogger('fileclean')
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
