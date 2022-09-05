from astropy.io import fits, ascii
from astropy.table import Table
import pandas as pd
import json
import numpy as np

from consts import EXT
from os import path, remove

import logging

class Extract:
    @classmethod
    def TTYPES(cls, header:dict):
        names = []
        for key,value in header.items():
            if key.startswith("TTYPE"):
                names.append(value)
        return names


class Utils:
    @classmethod
    def NormalizeArray(cls,header,data):
        result = {}
        for i in range(len(data)):
            result[f"{header}_{i+1}"] = data[i]       

        return result


class FITUtil:
    """
    FITS parser spesifically designed for Yuki Kaneko to display information in FITS files on a website.
    """
    def __init__(self,fits_path,fits_filename,temp_path) -> None:

        self.fits_path= fits_path
        self.fits_filename = fits_filename
        self.fits_corename = path.splitext(self.fits_filename)[0]

        self.json_path = ''
        self.json_basename = ''

        fits_fullpath = path.join(fits_path,fits_filename)
        self._fits = fits.open(fits_fullpath)

        self.temp_path = temp_path
    

    def parseEXT0(self) -> dict:
        """Parses Primary HDU header fields into a dictionary.

        Returns:
            dict: HDU0 as Dict 
        """
        HDU = self._fits[0]
        return dict(HDU.header)

    def parseEXT1(self) -> dict:
        """Parses Extension 1 HDU into dictionary, creates SIGNIFICANCE_x for every significance value in order to normalize.
        Values casted to float because numpy.floatings not JSON serializable.

        Returns:
            dict : HDU1 as Dict
        """
        result = {}        
        HDU:fits.BinTableHDU = self._fits[1]
        
        headers = Extract.TTYPES(dict(HDU.header))
        
        for header in headers:
            value = HDU.data[header][0]

            if header == "TRIG_DETS":
                #normalized = Utils.NormalizeArray(header,value)
                result[header] = [int(trig_value) for trig_value in value]
                #for sig_key, sig_value in normalized.items():
                #    result[sig_key] = float(sig_value)

            elif header == "SIGNIFICANCE":
                result[header] = [float(sig_value) for sig_value in value]

            else:
                result[header] = float(value)

        return result

    def parseEXT2(self) -> list:
        HDU:fits.BinTableHDU = self._fits[2]

        tbl:Table = Table.read(HDU)
        result = tbl.to_pandas().to_dict()

        return result


    def parseEXT3(self) -> dict:
        """Parses Extension 3 HDU and creates a dictionary.
        Keys are the CLASS_ARRAY fields and the values are the CLASS_PROBABILITY fields.

        Returns:
            dict: HDU3 as Dict
        """
        HDU:fits.BinTableHDU = self._fits[3]
        result = {}

        for value,name in HDU.data:
            name = name[0]
            result[name] = value  


        return result    

    def toJSON(self, seperate_HDUs = True) -> str:
        """Converts FITS file data into a JSON string.

        Args:
            seperate_HDUs (bool, optional): Should HDUs formatted seperately?. Defaults to True.

        Returns:
            str: JSON String
        """
        result = {}
        if seperate_HDUs:
            result = {
                "HDU0": self.parseEXT0(),
                "HDU1": self.parseEXT1(),
                "HDU3": self.parseEXT3()
            }
        else:
            result = {**self.parseEXT0(),**self.parseEXT1(),**self.parseEXT3()}


        self.json_basename = self.fits_corename + EXT.JSON
        dst_path = path.join(self.temp_path, self.json_basename)
        self.json_path = dst_path

        with open(dst_path,'w') as file:
            file.write(json.dumps(result))

    def deleteJSON(self):
        remove(path.join(self.temp_path,self.fits_corename + EXT.JSON))


    @classmethod
    def isFITS(cls,filename):
        return path.splitext(filename)[1] == EXT.FITS


if __name__ == '__main__':
    print("asdd")