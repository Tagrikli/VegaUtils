

class HIST:
    HISTORY_OLD = []
    HISTORY_NEW = []
    HISTORY_PATH = ''
    CNT = 0


    @classmethod
    def load(cls,cache_path):
        cls.HISTORY_PATH = cache_path

        try:
            with open(cls.HISTORY_PATH,'r') as file:
                cls.HISTORY_OLD = file.read().split('\n')
        except FileNotFoundError:
            open(cls.HISTORY_PATH,'x').close()

    @classmethod
    def exists(cls,filename):
        return filename in cls.HISTORY_OLD

    @classmethod
    def append(cls,filename):
        cls.HISTORY_NEW.append(filename)
        cls.CNT += 1
        if cls.CNT % 50 == 0:
            cls.save()
            cls.CNT = 0

    @classmethod
    def save(cls):
        with open(cls.HISTORY_PATH,'a') as file:
            for new_item in cls.HISTORY_NEW:
                file.write(f"{new_item}\n")

class LAST:
    LAST_PATH = ''
    LAST_FOLDER = ''

    @classmethod
    def load(cls,last_path):
        cls.LAST_PATH = last_path

        try:
            with open(cls.LAST_PATH,'r') as file:
                cls.LAST_FOLDER = file.read()
        except FileNotFoundError:
            open(cls.LAST_PATH,'x').close()

    @classmethod
    def get(cls):
        return cls.LAST_FOLDER

    @classmethod
    def set(cls,last_folder):
        cls.LAST_FOLDER = last_folder
        cls.save()


    @classmethod
    def save(cls):
        open(cls.LAST_PATH,'w').write(cls.LAST_FOLDER)
        
