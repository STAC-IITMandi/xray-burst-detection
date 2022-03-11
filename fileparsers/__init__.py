from . import read
from . import model

from astropy.table import Table
import datetime
import logging
import os

PATHBASE = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
DATA = Table(names=('id','upload_time','filename','status','message'), 
             dtype=(str,datetime.datetime,str,str,str))
UPLOAD_LIFETIME = datetime.timedelta(hours=24)

__all__ = ['read','DATA','analyse']

logger = logging.getLogger('fileparsers')


def analyse(id, params):
    logger.info(f"Beginning analysis for {id}")
    logger.info(params)
    fp = os.path.join(PATHBASE, 'uploads', id, 'raw')
    try : # Based on file hint
        if params['fileTypeHint'] == 'fits':
            ts, fs = read.fits(fp, params)
        elif params['fileTypeHint'] == 'xlsx':
            ts, fs = read.excel(fp, params)
        elif params['fileTypeHint'] == 'txt':
            ts, fs = read.text(fp, params)
        else : # Unrecognised files, try all methods
            for method in (read.fits, read.excel, read.text):
                try :
                    ts, fs = method(fp, params)
                    break
                except :
                    continue
            else :
                raise OSError('Could not understand the file format')
    except OSError as err :
        for row in DATA:
            if row['id']==id :
                row['status']='ERROR'
                row['message']=err.args[0]
                break
        return
    dts = read.timeformat(ts, params)

    parsed = Table((ts,dts,fs),names=('ts','dts','fs'))
    parsed.write(os.path.join(PATHBASE, 'uploads', id, 'timeseries.ecsv'), format='ascii')

    # Call model here
    # found_peaks = model.evaluate(ts, fs)
    
