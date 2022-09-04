import argparse
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


parser = argparse.ArgumentParser('File transition and transportation utilty for Vega.')
parser.add_argument('--debug',action='store',help="Use real paths or development paths.",nargs='*')
parser.add_argument('--upload',action='store',help='Upload to W4 or not.',nargs='*')

args = parser.parse_args()


logging.basicConfig(
    format='[%(asctime)s - %(funcName)s] -> %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


if args.debug is not None:
    BASE_DIR = BASE_DIR_DEV
    TEMP_DIR = TEMP_DIR_DEV



HIST.loadHistory(HIST_FILE)
logging.info('History loaded.')

if args.upload is not None:
    w4 = W4FTPS()
    w4.connect()
    logging.info('Connected to W4.')
    w4.login()
    logging.info('Logged in to W4.')


for pathe, dirs, files in os.walk(BASE_DIR,False):
    for file in files:

        if not fileIsValid(file):
            logging.info(f"{file:<30}- Not valid. Skipping.")
            continue


        common_name = commonName(file)
        if HIST.inHistory(common_name):
            logging.debug(f'{file:<30}- Already processed. Skipping.')
            continue


        logging.info(f"{common_name:<30}- Not in history.")

        if PSUtil.isPS(file):

            logging.info(f'{file:<30}- Processing')
            
            ps = PSUtil(pathe,file,TEMP_DIR)
                            
            ret = ps.toPDF()
            if ret:
                logging.info(f'{file:<30}- Converted to PDF.')

                dest_path = adaptPath(path.join(pathe,ps.pdf_basename))           

                if args.upload is not None:
                    w4.sendFile(ps.pdf_path,dest_path)
                    logging.info(f'{ps.pdf_basename:<30}- Sent to W4.')


                ps.deletePDF()
                logging.info(f'{ps.pdf_basename:<30}- Deleted.')
            else:
                ps.deletePDF()
                continue


        if FITUtil.isFITS(file):

            logging.info(f'{file:<30}- Processing')
            
            fit = FITUtil(pathe,file,TEMP_DIR)

            fit.toJSON()
            logging.info(f'{file:<30}- Converted to JSON.')

            dest_path = adaptPath(path.join(pathe,fit.json_basename))

            if args.upload is not None:
                w4.sendFile(fit.json_path,dest_path)
                logging.info(f'{file:<30}- Sent to W4.')

            fit.deleteJSON()
            logging.info(f'{file:<30}- Deleted.')

        HIST.append(common_name)
        logging.info(f'{common_name:<30}- Added to history.')


HIST.saveHistory()
logging.info(f'History saved.')

if args.upload is not None:
    w4.close()
    logging.info(f'W4 connection closed.')