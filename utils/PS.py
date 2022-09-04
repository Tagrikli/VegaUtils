from os import remove,path
from subprocess import run
from consts import EXT

import logging

class PSUtil:
    def __init__(self,ps_path,ps_filename,temp_path) -> None:
        self.ps_path = ps_path
        self.ps_filename = ps_filename
        self.ps_corename = path.splitext(self.ps_filename)[0]

        self.pdf_path = ''
        self.pdf_basename = ''

        self.temp_path = temp_path            


    def toPDF(self):

        self.pdf_basename = self.ps_corename + EXT.PDF
        src_path = path.join(self.ps_path, self.ps_filename)
        dst_path = path.join(self.temp_path,self.pdf_basename)        
        self.pdf_path = dst_path

        p = run(['ps2pdf',src_path,dst_path])
        if p.returncode != 0:
            logging.error(f"{self.ps_filename:<30} Processing Failed")
            return False

        return True


    def deletePDF(self):
        remove(path.join(self.temp_path,self.ps_corename + EXT.PDF))

    @classmethod
    def isPS(cls,filename):
        return path.splitext(filename)[1] == EXT.PS