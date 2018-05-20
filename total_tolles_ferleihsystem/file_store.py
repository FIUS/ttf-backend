"""
This module contains all file handling options
"""

import os

# pylint: disable=E0611
from hashlib import sha3_256
from typing import Tuple, List
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from werkzeug.datastructures import FileStorage

from . import APP


Hash = str


TMP_DOWNLOAD_FILE_NAME = 'data.upload'
TMP_DATA_FILE_NAME = 'data.tmp'
TMP_ARCHIVE_FILE_NAME = 'archive.tmp'
DATA_FILE_NAME = 'file-store.dat'

TMP_FOLDER = APP.config['TMP_DIRECTORY']
DATA_FOLDER = APP.config['DATA_DIRECTORY']

TMP_DOWNLOAD_FILE_PATH = os.path.join(TMP_FOLDER, TMP_DOWNLOAD_FILE_NAME)
TMP_DATA_FILE_PATH = os.path.join(TMP_FOLDER, TMP_DATA_FILE_NAME)
TMP_ARCHIVE_FILE_PATH = os.path.join(TMP_FOLDER, TMP_ARCHIVE_FILE_NAME)
DATA_FILE_PATH = os.path.join(DATA_FOLDER, DATA_FILE_NAME)


def save_file(file: FileStorage) -> Hash:
    """
    Save a file from a flask endpoint3
    """
    file.save(TMP_DOWNLOAD_FILE_PATH)
    with open(TMP_DOWNLOAD_FILE_PATH, 'rb') as tmp_file:
        file_hash = sha3_256(tmp_file.read()).hexdigest()

    _store(TMP_DOWNLOAD_FILE_PATH, file_hash)
    return file_hash


def _store(file_path: os.PathLike, file_hash: Hash) -> None:
    with ZipFile(DATA_FILE_PATH, 'ab', ZIP_STORED, True) as data_file:
        data_file.write(file_path, file_hash)


def read_file(file_hash: str) -> bytes:
    """
    Read a file in the store via it's hash
    """
    with ZipFile(DATA_FILE_PATH, 'rb', ZIP_STORED, True) as data_file:
        return data_file.read(file_hash)


def create_archive(files: List[Tuple[Hash, str]]) -> Hash:
    """
    Create a archive collection full of files from the store
    """
    with ZipFile(TMP_ARCHIVE_FILE_PATH, 'wb', ZIP_DEFLATED) as tmp_archive:
        for file in files:
            with open(TMP_DATA_FILE_PATH, 'wb') as data_file:
                data_file.write(read_file(file[0]))
            tmp_archive.write(TMP_DATA_FILE_PATH, file[1])
    with open(TMP_ARCHIVE_FILE_PATH, 'rb') as tmp_archive:
        file_hash = sha3_256(tmp_archive.read()).hexdigest()

    _store(TMP_ARCHIVE_FILE_PATH, file_hash)
    return file_hash
