import os

class BaseConfig(object):
    pass

class DevConfig(BaseConfig):
    FILE_PATH = os.path.join(os.getcwd(), 'files')

class ProdConfig(BaseConfig):
    FILE_PATH = '/home/dfhack/files'
    USE_X_SENDFILE = True
