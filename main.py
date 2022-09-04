import argparse
import multiprocessing
import sys
import os
from os import path
import logging
from config import BASE_DIR, BASE_DIR_DEV, HIST_FILE,TEMP_DIR,TEMP_DIR_DEV, CORE
from utils.FTP_TLS import W4FTPS, Explicit_FTP_TLS
from utils.FITS import FITUtil
from utils.PS import PSUtil
from utils.General import adaptPath, commonName, fileIsValid
from utils.History import HIST
from multiprocessing import Pool,Queue
import progressbar

parser = argparse.ArgumentParser('File transition and transportation utilty for Vega.')
parser.add_argument('--debug',action='store',help="Use real paths or development paths.",nargs='*')
parser.add_argument('--upload',action='store',help='Upload to W4 or not.',nargs='*')

args = parser.parse_args()

logging.basicConfig(
    format='[%(asctime)s - %(funcName)s] -> %(message)s',
    level=logging.ERROR,
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

queue = Queue()


def Init():
    global w4
    w4 = W4FTPS()
    w4.connect()
    logging.info('Connected to W4.')
    w4.login()
    logging.info('Logged in to W4.')

def Process(file_full):


    pathe = os.path.dirname(file_full)
    file = os.path.basename(file_full)

    if not fileIsValid(file):
        logging.info(f"{file:<30}- Not valid. Skipping.")
        return

    common_name = commonName(file)
    if HIST.inHistory(common_name):
        logging.debug(f'{file:<30}- Already processed. Skipping.')
        return


    logging.info(f"{common_name:<30}- Not in history.")



    if PSUtil.isPS(file):

        logging.info(f'{file:<30}- Processing')
        
        ps = PSUtil(pathe,file,TEMP_DIR)
                        
        ret = ps.toPDF()
        if ret:
            logging.info(f'{file:<30}- Converted to PDF.')

            dest_path = adaptPath(os.path.join(pathe,ps.pdf_basename))           

            w4.sendFile(ps.pdf_path,dest_path)
            logging.info(f'{ps.pdf_basename:<30}- Sent to W4.')


            ps.deletePDF()
            logging.info(f'{ps.pdf_basename:<30}- Deleted.')
        else:
            ps.deletePDF()
            return


    if FITUtil.isFITS(file):

        logging.info(f'{file:<30}- Processing')
        
        fit = FITUtil(pathe,file,TEMP_DIR)

        fit.toJSON()
        logging.info(f'{file:<30}- Converted to JSON.')

        dest_path = adaptPath(os.path.join(pathe,fit.json_basename))

        w4.sendFile(fit.json_path,dest_path)
        logging.info(f'{file:<30}- Sent to W4.')

        fit.deleteJSON()
        logging.info(f'{file:<30}- Deleted.')



    return common_name


total_files = []

for path,dirs,files in os.walk(BASE_DIR):

    for file in files:
        total_files.append(os.path.join(path,file))


widgets = ['Processing...', progressbar.Bar('*'), progressbar.Percentage()]
bar = progressbar.ProgressBar(max_value=len(total_files),widgets=widgets).start()

processed = 0

pool = Pool(CORE, Init)
for result in pool.imap(Process,total_files):
    if result:
        HIST.append(result)

    processed += 1
    bar.update(processed)

w4.close()
HIST.saveHistory()
exit()


for index in range(0,len(total_files),core):

    chunk = total_files[index: index + core]
    procs = []
    for file in chunk:
        p = multiprocessing.Process(target=Process,args=(file,))
        p.start()
        procs.append(p)
        
    [proc.join() for proc in procs]
    
    common_names = [commonName(file) for file in chunk]

    HIST.append(common_names)

    #logging.info(f'{common_name:<30}- Added to history.')
    processed += len(chunk)
    bar.update(processed)       


HIST.saveHistory()
logging.info(f'History saved.')
