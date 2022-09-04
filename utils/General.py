from subprocess import check_output,run
from config import BASE_LAST, W4_PATH
from os import path,remove




def commonName(filename):
    corename = path.splitext(filename)[0].replace('_12det','').replace('_8cha','')
    return corename


def adaptPath(src_path:str):
    to_mount = src_path.split(BASE_LAST)[-1]
    return path.normpath(W4_PATH + to_mount)


def findFilesByExt(base_path,extension):
    output = check_output(f"find {base_path} -name *.{extension}", shell=True)
    result = output.decode('utf8').split('\n')
    return result

