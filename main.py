import argparse
from distutils.debug import DEBUG
from distutils.log import INFO
import sys
import os
from os import path
import logging
from turtle import exitonclick
from config import BASE_DIR, BASE_DIR_DEV, HIST_FILE,TEMP_DIR,TEMP_DIR_DEV
from utils.FTP_TLS import W4FTPS, Explicit_FTP_TLS
from utils.FITS import FITUtil
from utils.PS import PSUtil
from utils.General import adaptPath, commonName, fileIsValid
from utils.History import HIST
import progressbar


# Argument parsing
parser = argparse.ArgumentParser('File transition and transportation utilty for Vega.')
parser.add_argument('--debug',action='store',help="Use real paths or development paths.",nargs='*')
parser.add_argument('--upload',action='store',help='Upload to W4 or not.',nargs='*')
parser.add_argument('--scan-only',action='store',help='Scan folders.',nargs='*')
parser.add_argument('--reupload-all',action='store',help="Re-upload all files.",nargs="*")
parser.add_argument('--verbose',action='store',nargs="*")
args = parser.parse_args()



# Logging configuration

LOG_LEVEL = logging.DEBUG if args.verbose is not None else logging.INFO

logging.basicConfig(
    format='[%(asctime)s] -> %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.FileHandler("debug.log"),
    ],
)


# Progressbar setup
widgets = ["Processed:",progressbar.Bar('#'),progressbar.Percentage()]
progress_bar = progressbar.ProgressBar(widgets=widgets)

# Enable debug paths if its the case.
if args.debug is not None:
    BASE_DIR = BASE_DIR_DEV
    TEMP_DIR = TEMP_DIR_DEV


if args.reupload_all is not None:
    try:
        os.remove(path.abspath(HIST_FILE))
        logging.info("History file deleted.")
    except:
        logging.error("History file cannot be deleted.")


HIST.load(HIST_FILE)
logging.info('History loaded.')

# FTP_TLS connection setup
if args.upload is not None:
    try:
        w4 = W4FTPS()
        w4.connect()
        logging.info('Connected to W4.')
        w4.login()
        logging.info('Logged in to W4.')
    except:
        logging.error("Something wrong with FTP Init.")
        exit()


# Folder scan
print()
print("Folders are scanning...")

files_to_process = []
file_count_not_processed = 0

file_count_processed = 0
file_count_invalid = 0

for path, dirs, files in os.walk(BASE_DIR,False):
    for file in files:

        # If file is not valid. (Check regex)
        if not fileIsValid(file):
            logging.info(f"{file:<30}- Not valid.")
            file_count_invalid += 1
            continue


        # If file already processed.
        if HIST.exists(file):
            logging.debug(f'{file:<30}- Already processed.')
            file_count_processed += 1
            continue       

        logging.info(f"{file:<30}- Not in history.")
        files_to_process.append(os.path.join(path,file))

file_count_not_processed = len(files_to_process)

print(f"""
--------- SCAN RESULT --------
Processed count:        {file_count_processed}
Invalid file count:     {file_count_invalid}
Not Processed count:    {file_count_not_processed}
""")

if args.scan_only is not None:
    exit()

if file_count_not_processed == 0:
    print("Nothing to do. Bye!")
    exit()

print("Files are being processed...")

progress_bar.start(file_count_not_processed)

for i,file_path in enumerate(files_to_process):

    path = os.path.dirname(file_path)
    file = os.path.basename(file_path)
    

    if PSUtil.isPS(file):

        logging.info(f'{file:<30}- Processing')
        
        ps = PSUtil(path,file,TEMP_DIR)
                        
        ret = ps.toPDF()
        if ret:
            logging.info(f'{file:<30}- Converted to PDF.')

            dest_path = adaptPath(os.path.join(path,ps.pdf_basename))           

            if args.upload is not None:
                w4.sendFile(ps.pdf_path,dest_path)
                logging.info(f'{ps.pdf_basename:<30}- Sent to W4.')


            ps.deletePDF()
            logging.info(f'{ps.pdf_basename:<30}- Deleted.')
        else:
            logging.error(f"{file:<30} PS to PDF Error.")
            ps.deletePDF()
            continue


    if FITUtil.isFITS(file):

        logging.info(f'{file:<30}- Processing')
        
        fit = FITUtil(path,file,TEMP_DIR)

        fit.toJSON()
        logging.info(f'{file:<30}- Converted to JSON.')

        dest_path = adaptPath(os.path.join(path,fit.json_basename))

        if args.upload is not None:
            w4.sendFile(fit.json_path,dest_path)
            logging.info(f'{file:<30}- Sent to W4.')

        fit.deleteJSON()
        logging.info(f'{file:<30}- Deleted.')


    HIST.append(file)
    logging.info(f'{file:<30}- Added to history.')

    progress_bar.update(i)

print("Processing finished.")

HIST.save()
logging.info(f'History saved.')

if args.upload is not None:
    w4.close()
    logging.info(f'W4 connection closed.')
