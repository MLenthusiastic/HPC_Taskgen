import json
import os
import time
import platform
import logging
import logging.handlers

PLATFORM_WINDOWS = 'Windows'

if platform.system() == PLATFORM_WINDOWS:
    # conda install -c anaconda pywin32
    import win32file, win32con, pywintypes
else:
    import fcntl

class LoggingUtils(object):

    def __init__(self, name):
        self.report_name = name
        self.my_logger = logging.getLogger('MyLogger')
        self.my_logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(self.report_name, mode='w')
        self.my_logger.addHandler(handler)








