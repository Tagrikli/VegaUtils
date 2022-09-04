from subprocess import check_output,run
from config import BASE_LAST, W4_PATH
from os import path,remove
import re


def fileIsValid(filename):
    s = re.search(r'^[BPS][1-4]_[0-9]{6}_[0-9]{2}_(12det_|8cha_)?[0-9]{1,5}\.(ps|fit)$',filename)
    return s is not None


def commonName(filename):
    corename = path.splitext(filename)[0].replace('_12det','').replace('_8cha','')
    corename = path.basename(corename)
    return corename



def adaptPath(src_path:str):
    to_mount = src_path.split(BASE_LAST)[-1]
    return path.normpath(W4_PATH + to_mount)


def findFilesByExt(base_path,extension):
    output = check_output(f"find {base_path} -name *.{extension}", shell=True)
    result = output.decode('utf8').split('\n')
    return result

