import os

SITE_NAME = 'Files'
FILE_PATH = os.path.join(os.getcwd(), 'files')

try:
    from local_config import *
except ImportError:
    pass
