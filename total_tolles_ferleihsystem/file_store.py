"""
This module contains all file handling options
"""

import os
from zipfile import ZipFile
import hashlib
from . import APP


TMP_FILE_NAME = 'ttf.upload'
DATA_FILE_NAME = 'file-store.dat'

TMP_FOLDER_PATH = APP.config['TMP_DIRECTORY']
DATA_FOLDER_PATH = APP.config['DATA_DIRECTORY']

TMP_FILE_PATH = os.path.join(TMP_FOLDER_PATH, TMP_FILE_NAME)
DATA_FILE_PATH = os.path.join(DATA_FOLDER_PATH, DATA_FILE_NAME)


def save_file(file):
    """
    Save a file from a flask endpoint
    """
    file.save(TMP_FILE_PATH)
    with open(TMP_FILE_PATH, 'rb') as tmp_file:
        # pylint: disable=E1101
        file_hash = hashlib.sha3_256(tmp_file.read()).hexdigest()
    with ZipFile(DATA_FILE_PATH, 'a') as data_file:
        data_file.write(TMP_FILE_PATH, file_hash)

    return file_hash


def read_file(file_hash):
    """
    Read a file in the store via it's hash
    """
    with ZipFile(DATA_FILE_PATH, 'r') as data_file:
        return data_file.read(file_hash)
