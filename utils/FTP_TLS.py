import ftplib
from ftplib import all_errors
from pathlib import Path
from consts import FTP_ERROR

from config import W4_PASS, W4_PATH, W4_USER
from os import path


class Explicit_FTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)
        return conn, size


class W4FTPS:

    def connect(self):
        self.ftp = Explicit_FTP_TLS('w4')


    def login(self):
        self.ftp.login(W4_USER,W4_PASS)
        self.ftp.prot_p()
    

    def mkdir(self,dst):


        try:
            self.ftp.mkd(dst)
        except all_errors as e:

            error_msg = self.__error_msg(e)

            if error_msg == FTP_ERROR.NO_SUCH_FILE_OR_DIR:
                parent_path = path.dirname(dst)
                self.mkdir(parent_path)


            elif error_msg == FTP_ERROR.FILE_EXISTS:
                return


            self.ftp.mkd(dst)



    def sendFile(self,src,dest):

        with open(src,'rb') as file:
            try:
                self.ftp.storbinary(f'STOR {dest}',file)
            except all_errors as e:

                error_msg = self.__error_msg(e)

                if error_msg == FTP_ERROR.NO_SUCH_FILE_OR_DIR:
                    self.mkdir(path.dirname(dest))
            
                    self.ftp.storbinary(f'STOR {dest}',file)

                else:
                    print("Oh no", error_msg)


    def __error_msg(self,error):
        return (str(error).split(':')[-1]).strip()

    def close(self):
        self.ftp.close()


if __name__ == "__main__":

    w4 = W4FTPS()
    w4.connect()
    w4.login()

    ftp = w4.ftp

    w4.mkdir('/deneme/allah/selam/annen')

    w4.close()

