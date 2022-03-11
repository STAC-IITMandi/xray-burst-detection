from __future__ import annotations

from astropy.io import fits as FITSio, ascii as ASCIIio
from openpyxl import load_workbook
import numpy as np

import sys
import logging
import datetime

logger = logging.getLogger('fileparsers.read')


def fits(file:str, params:dict) -> tuple[np.ndarray, np.ndarray]:
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
        return (ts_col, fl_col)
    except Exception as e :
        logger.error(f'FITS Parser for {file} error - '+' '.join(map(str,e.args)))
        raise OSError(error_msg)


def text(file:str, params:dict) -> tuple[np.ndarray, np.ndarray]:
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
        return (ts_col, fl_col)
    except Exception as e :
        logger.error(f'ASCII Parser for {file} error - '+' '.join(map(str,e.args)))
        raise OSError(error_msg)
    
    
def excel(file:str, params:dict) -> tuple[np.ndarray, np.ndarray]:
    try :
        error_msg = 'Could not open the file in XLSX format'
        ff = load_workbook(file)
        error_msg = f'Could not locate the sheet named {params["fMeta_tableName"]}'
        ws = ff[params["fMeta_tableName"]]
        error_msg = 'Could not find or parse time series column in the Excel table'
        for timecol in ws.columns :
            if timecol[0].value == params['fMeta_timeSerName']:
                ts_col = np.array([float(x.value) for x in timecol[1:] if x])
                break
        error_msg = 'Could not find or parse flux series column in the Excel table'
        for fluxcol in ws.columns :
            if fluxcol[0].value == params['fMeta_fluxSerName']:
                fl_col = np.array([float(x.value) for x in timecol[1:] if x])
                break
        return (ts_col, fl_col)
    except Exception as e :
        logger.error(f'ASCII Parser for {file} error - '+' '.join(map(str,e.args)))
        raise OSError(error_msg)


def timeformat(ts:np.ndarray[float], params:dict)  -> np.ndarray[np.datetime64]:
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
