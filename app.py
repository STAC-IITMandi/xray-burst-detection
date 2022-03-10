
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv

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
app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(hours=24),
    SESSION_REFRESH_EACH_REQUEST=False,
)
UPLOAD_TIMES = {}

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
        print(request.files)
        d = os.path.join(PATHBASE, 'uploads', id)
        if not os.path.isdir(d):
            os.mkdir(d)
        f.save(os.path.join(d,'raw'))
        UPLOAD_TIMES[id] = datetime.datetime.now()
        logger.info(f"Created file {id}")
        return render_template('base.html')



def cleaner():
    global app, PATHBASE, UPLOAD_TIMES
    logger = logging.getLogger('fileclean')
    while True :
        x = []
        for id, t in UPLOAD_TIMES.items() :
            if datetime.datetime.now() > t + app.config['PERMANENT_SESSION_LIFETIME'] :
                try :
                    shutil.rmtree(os.path.join(PATHBASE, 'uploads', id), ignore_errors=True)
                    x.append(id)
                    logger.info(f"Deleted {id}")
                except :
                    logger.exception(f"Couldn't delete {id}")
        for id in x :
            UPLOAD_TIMES.pop(id)
        time.sleep(60 * 5)



if __name__ == '__main__':
    _debug = os.environ.get('DEBUG','').lower() == 'true'
    _cleanerprocess = threading.Thread(target=cleaner)
    _cleanerprocess.start()
    app.run(host='0.0.0.0', port=5000, debug=_debug)
