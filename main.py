import sys
import os
from os import path
import logging
from config import BASE_DIR, BASE_DIR_DEV, HIST_FILE,TEMP_DIR,TEMP_DIR_DEV
from utils.FTP_TLS import W4FTPS, Explicit_FTP_TLS
from utils.FITS import FITUtil
from utils.PS import PSUtil
from utils.General import adaptPath, commonName, fileIsValid
from utils.History import HIST



logging.basicConfig(
    format='[%(asctime)s - %(funcname)s] -> %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    BASE_DIR = BASE_DIR_DEV
    TEMP_DIR = TEMP_DIR_DEV


HIST.loadHistory(HIST_FILE)
logging.debug('History loaded.')

w4 = W4FTPS()
w4.connect()
logging.debug('Connected to W4.')
w4.login()
logging.debug('Logged in to W4.')


for pathe, dirs, files in os.walk(BASE_DIR,False):
    for file in files:

        if not fileIsValid(file):
            logging.debug(f"{file:<30}- Not valid. Skipped.")
            continue

        common_name = commonName(file)

        if not HIST.inHistory(common_name):

            logging.debug(f"{common_name:<30}- Not in history.")

            if PSUtil.isPS(file):

                logging.debug(f'{file:<30}- Processing')
                
                ps = PSUtil(pathe,file,TEMP_DIR)
                                
                ret = ps.toPDF()
                if ret:
                    logging.debug(f'{file:<30}- Converted to PDF.')

                    dest_path = adaptPath(path.join(pathe,ps.pdf_basename))           

                    #w4.sendFile(ps.pdf_path,dest_path)
                    logging.debug(f'{ps.pdf_basename:<30}- Sent to W4.')


                    #ps.deletePDF()
                    logging.debug(f'{ps.pdf_basename:<30}- Deleted.')
                else:
                    continue


            if FITUtil.isFITS(file):

                logging.debug(f'{file:<30}- Processing')
                
                fit = FITUtil(pathe,file,TEMP_DIR)

                fit.toJSON()
                logging.debug(f'{file:<30}- Converted to JSON.')

                dest_path = adaptPath(path.join(pathe,fit.json_basename))

                #w4.sendFile(fit.json_path,dest_path)
                logging.debug(f'{file:<30}- Sent to W4.')

                #fit.deleteJSON()
                logging.debug(f'{file:<30}- Deleted.')

            HIST.append(common_name)
            logging.debug(f'{common_name:<30}- Added to history.')

        else:
            logging.debug(f'{file:<30}- Already processed.')


HIST.saveHistory()
logging.debug(f'History saved.')


w4.close()
logging.debug(f'W4 connection closed.')