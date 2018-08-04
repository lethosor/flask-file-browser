import os

FILE_PATH = os.path.join(os.getcwd(), 'files')

try:
    from local_config import *
except ImportError:
    pass
