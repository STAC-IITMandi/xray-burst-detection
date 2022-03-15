"""
All functions to parse data from an input file in a specific format are defined here.

The logic is more complex than in the `write` module as the algorithms try best to find the data in any kind
of file based on all the given user input.
At each stage, the `error_msg` that is set will be displayed on the frontend if the following statement fails.
(Exception will be caught, file parse status marked as "ERROR" in the `DATA` table, and a dialog displayed on the webpage.)
"""


from astropy.io import fits as FITSio, ascii as ASCIIio
from openpyxl import load_workbook
import numpy as np

import sys
import logging
import datetime

logger = logging.getLogger('fileparsers.read')


def fits(file:str, params:dict) :
    try :
        error_msg = 'Could not open the file in FITS format'
        ff = FITSio.open(file)
        error_msg = f'Could not locate the FITS HDU table named {params["fMeta_tableName"]}'
        if params['fMeta_tableName'] in ff :
            table = ff[params['fMeta_tableName']].data
        else :
            for hdu in ff:
                if isinstance(hdu, fits.hdu.table.BinTableHDU):
                    table = hdu.data
                    break
            else :
                error_msg = 'Could not locate any Binary HDU table in FITS file'
                raise ValueError
        
        error_msg = 'Could not find time series column in the FITS table'
        ts_col = table[params['fMeta_timeSerName']]
        error_msg = 'Could not find flux series column in the FITS table'
        fl_col = table[params['fMeta_fluxSerName']]
        err_col = table[params['fMeta_errSerName']] if params['fMeta_errSerName'] \
            in table.columns.names else None
        
        error_msg = 'Partial records / Unequal number of time & flux observations'
        if len(ts_col) != len(fl_col):
            raise ValueError
        if err_col is not None and len(err_col) != len(ts_col):
            err_col = None
        
        return (ts_col, fl_col, err_col)

    except Exception as e :
        logger.error(f'FITS Parser for {file} error - '+' '.join(map(str,e.args)))
        raise OSError(error_msg)




def text(file:str, params:dict) :
    try :
        for method in ('csv','tab','basic','fixed_width','commented_header','html',):
            try :
                ff = ASCIIio.read(file, guess=False, method=method)
                break
            except: 
                continue
        else :
            error_msg = 'Could not open the file in any well-known ASCII table format'
            if 'fMeta_asciiDelim' in params :
                ff = ASCIIio.read(file, delimiter=params.get('fMeta_asciiDelim'))
            else :
                ff = ASCIIio.read(file)
        
        error_msg = 'Could not find time series column in the ASCII table'
        ts_col = ff[params['fMeta_timeSerName']].value
        error_msg = 'Could not find flux series column in the ASCII table'
        fl_col = ff[params['fMeta_fluxSerName']].value
        err_col = ff[params['fMeta_errSerName']].value if params['fMeta_errSerName'] in ff else None
        
        error_msg = 'Partial records / Unequal number of time & flux observations'
        if len(ts_col) != len(fl_col):
            raise ValueError
        if err_col is not None and len(err_col) != len(ts_col):
            err_col = None
        
        return (ts_col, fl_col, err_col)

    except Exception as e :
         # limit because ascii module dumps entire file content into error messgae
        ers = ' '.join(map(str,e.args))[:2000]
        logger.error(f'ASCII Parser for {file} error - '+ers)
        raise OSError(error_msg)



    
def excel(file:str, params:dict) :
    try :
        error_msg = 'Could not open the file in XLSX format'
        ff = load_workbook(file)
        error_msg = f'Could not locate the sheet named {params["fMeta_tableName"]}'
        if params["fMeta_tableName"] in ws :
            ws = ff[params["fMeta_tableName"]]
        else :
            ws = ff.worksheets[0]
        
        error_msg = 'Could not find or parse time series column in the Excel table'
        for timecol in ws.columns :
            if timecol[0].value == params['fMeta_timeSerName']:
                ts_col = np.array([float(x.value) for x in timecol[1:] if x])
                break
        else :
            raise ValueError
        error_msg = 'Could not find or parse flux series column in the Excel table'
        for fluxcol in ws.columns :
            if fluxcol[0].value == params['fMeta_fluxSerName']:
                fl_col = np.array([float(x.value) for x in fluxcol[1:] if x])
                break
        else :
            raise ValueError
        
        for errcol in ws.columns :
            if errcol[0].value == params['fMeta_errSerName']:
                errcol = np.array([float(x.value) for x in errcol[1:] if x])
                break
        else :
            errcol = None
        
        error_msg = 'Partial records / Unequal number of time & flux observations'
        if len(ts_col) != len(fl_col):
            raise ValueError
        if err_col is not None and len(err_col) != len(ts_col):
            err_col = None
        
        return (ts_col, fl_col, err_col)

    except Exception as e :
        logger.error(f'ASCII Parser for {file} error - '+' '.join(map(str,e.args)))
        raise OSError(error_msg)





def timeformat(ts:np.ndarray, params:dict) :
    """Try to convert times given as running count from an epoch (eg 18100721.0)
    into ISO formatted datetime strings. 
    This is for convenience while being displayed on the graph/visualisation"""
    try :
        unit = float(params['fMeta_timeUnit'])
    except :
        unit = 1
    try :
        d = ts.astype(np.timedelta64(1,'s')) * unit
        t = d + np.datetime64(datetime.datetime.fromisoformat(params['fMeta_timeEpoch']))
        return t
    except Exception as e :
        logger.error('Timestamp conversion error'+' '.join(map(str,e.args)))
        return ts
