

class HIST:
    HISTORY_OLD = []
    HISTORY_NEW = []
    HISTORY_PATH = ''


    @classmethod
    def loadHistory(cls,cache_path):
        cls.HISTORY_PATH = cache_path

        try:
            with open(cls.HISTORY_PATH,'r') as file:
                cls.HISTORY_OLD = file.read().split('\n')
        except FileNotFoundError:
            open(cls.HISTORY_PATH,'x').close()

    @classmethod
    def inHistory(cls,filename):
        return filename in cls.HISTORY_OLD

    @classmethod
    def append(cls,filename):
        cls.HISTORY_NEW.append(filename)

    @classmethod
    def saveHistory(cls):
        with open(cls.HISTORY_PATH,'a') as file:
            for new_item in cls.HISTORY_NEW:
                file.write(f"{new_item}\n")

