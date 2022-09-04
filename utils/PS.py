from os import remove,path
from subprocess import run
from consts import EXT
from config import *

class PSUtil:
    def __init__(self,ps_path,ps_filename,debug=False) -> None:
        self.ps_path = ps_path
        self.ps_filename = ps_filename
        self.ps_corename = path.splitext(self.ps_filename)[0]
        self.temp_path = TEMP_PATH

        self.pdf_path = ''
        self.pdf_basename = ''

        if debug:
            self.temp_path = TEMP_PATH_DEV            


    def toPDF(self):

        self.pdf_basename = self.ps_corename + EXT.PDF
        src_path = path.join(self.ps_path, self.ps_filename)
        dst_path = path.join(self.temp_path,self.pdf_basename)        
        self.pdf_path = dst_path

        p = run(['ps2pdf',src_path,dst_path])
        return p.returncode    


    def deletePDF(self):
        remove(path.join(self.temp_path,self.ps_corename + EXT.PDF))

    @classmethod
    def isPS(cls,filename):
        return path.splitext(filename)[1] == EXT.PS