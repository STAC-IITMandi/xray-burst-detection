"""
The fileparsers module is the intermediary between the webserver and the statistical model.
The bulk of the code of the entire app is here, and is just to handle all the different
input and output formats.

More input formats can be supported by :
- Defining a function for the filetype in `./read.py`
- Optionally allow recognizing it in the front-end itself in `static/upload.js`
- Calling that read function here in part 1 of the `analyse` function

More output formats can be supported by :
- Defining a function for the filetype in `./write.py`
- Calling that write function here in part 4 of the `analyse` function
- Adding a clause to the query for URL `/data/result/<id>?format=filetype`
  in `data_server` in `app.py`, to serve the generated output file.
"""


import os
import sys
PATHBASE = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(PATHBASE)

from . import read
from . import write
import model


from astropy.table import Table
import numpy as np
import datetime
import logging
import json

UPLOAD_LIFETIME = datetime.timedelta(hours=24)
DATA = Table(names=('id','upload_time','filename','status','message','error_included'), 
             dtype=(str,datetime.datetime,'object',str,'object',bool))
"""
This table `DATA` serves as a storage for metadata of the status of all uploads presently
on the server, used by this module & app.py to track the files.
"""

__all__ = ['read','write','DATA','analyse']

logger = logging.getLogger('fileparsers')


def analyse(id, params):
    """
    1. Try parsing the saved input (raw) file using all the appropriate parsers in the `read` module.
    2. Save the extracted time (converted to ISO datetime if possible), Flux, and (optional) error columns
       to a common CSV format acceptable by the frontend graph visualisation library
    3. Pass the extracted time (original) and Flux series to the Statistical algorithm (`model.evaluate`)
       and receive the list of bursts detected.
    4. Save the burst info to all formats defined in the `write` module, for download by the user.
       Also save as JSON for graph plotting in the frontend.
    """
    logger.info(f"Beginning analysis for {id}")
    logger.info(params)
    fp = os.path.join(PATHBASE, 'uploads', id, 'raw')

    # *********** 1 ***********
    try : # Based on file hint
        if params['fileTypeHint'] == 'fits':
            ts, fs, er = read.fits(fp, params)
        elif params['fileTypeHint'] == 'xlsx':
            ts, fs, er = read.excel(fp, params)
        elif params['fileTypeHint'] == 'txt':
            ts, fs, er = read.text(fp, params)
        else : # Unrecognised files, try all methods
            for method in (read.fits, read.excel, read.text):
                try :
                    ts, fs, er = method(fp, params)
                    break
                except :
                    continue
            else :
                raise OSError('Could not understand the file format')
    
    except OSError as err :
        for row in DATA:
            if row['id']==id :
                row['status'], row['message'] = 'ERROR', err.args[0]
                break
        return
    
    dts = read.timeformat(ts, params)
    logger.info(f"Finished reading input file {id}")

    # *********** 2 ***********
    for row in DATA:
        if row['id']==id :
            row['status'], row['message'], row['error_included'] = 'OK', '', er is not None
            break
    write.timeseries(
        os.path.join(PATHBASE, 'uploads', id, 'timeseries.csv'),
        dts, fs, er
    )
    logger.info(f"Finished writing timeseries CSV file {id}")


    # *********** 3 ***********
    try :
        # Call model here
        found_peaks = model.evaluate(ts, fs)

        for peak in found_peaks :
            times = peak['start_time'], peak['end_time'], peak['max_time']
            sdt, edt, mdt = map(str, read.timeformat(np.array(times), params))
            peak['start_time'], peak['end_time'], peak['max_time'] = sdt, edt, mdt
    except Exception as err :
        logger.exception(f"Statistical model failed to run - {id}")
        with open(os.path.join(PATHBASE, 'uploads', id, 'result.json'), 'w') as rfile :
            json.dump({'status':'ERROR', 'message':err.args[0]}, rfile)
        return
    logger.info(f"Model call finished for {id}")


    # *********** 4 ***********
    fname, fdate = '', ''
    for row in DATA:
        if row['id']==id :
            fname, fdate = row['filename'], row['upload_time'].isoformat()
            break
    with open(os.path.join(PATHBASE, 'uploads', id, 'result.json'), 'w') as rfile :
        json.dump({'status':'OK', 'message':'', 
                  'metadata' : {
                        'filename': fname,
                        'upload_date': fdate,
                        'software': 'X-Ray burst detector',
                        'software_URL': 'https://github.com/InterIIT2022-ISRO-T3/MP_ISRO_T3',
                  },
                  'BURSTS':found_peaks}, rfile)
    logger.info(f"Wrote JSON result - {id}")

    try :
        write.fits(found_peaks, 
            os.path.join(PATHBASE, 'uploads', id, 'result.fits'),
            fname, fdate)
        logger.info(f"Wrote FITS result - {id}")
    except Exception as err :
        logger.exception(f"Error writing results to fits format - {id}")
    try :
        write.excel(found_peaks, 
            os.path.join(PATHBASE, 'uploads', id, 'result.xlsx'),
            fname, fdate)
        logger.info(f"Wrote XLSX result - {id}")
    except Exception as err :
        logger.exception(f"Error writing results to excel format - {id}")
    try :
        write.text(found_peaks, 
            os.path.join(PATHBASE, 'uploads', id, 'result.csv'),
            fname, fdate)
        logger.info(f"Wrote CSV result - {id}")
    except Exception as err :
        logger.exception(f"Error writing results to csv format - {id}")
    
