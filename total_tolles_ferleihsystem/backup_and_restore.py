"""
This module contains all functions and code needed to backup or restore the system.
"""

import os
from zipfile import ZipFile, ZIP_STORED
from sqlalchemy.exc import IntegrityError

from . import APP, DB
from .db_models.item import File

@APP.cli.command('create_backup') # TODO add flag to select to backup files aswell
def create_backup():
    # FIXME implement this!
    pass

@APP.cli.command('import_backup')
def import_backup():
    # FIXME implement this!
    pass

@APP.cli.command('upgrade_dataset')
def upgrade_dataset() -> None:
    DATA_FILE_NAME = 'file-store.dat'
    DATA_FOLDER = APP.config['DATA_DIRECTORY']
    DATA_FILE_PATH = os.path.join(DATA_FOLDER, DATA_FILE_NAME)

    _import_data_zipfile(DATA_FILE_PATH)

def _import_data_zipfile(zipfile) -> None:
    """
    Helper function to load all files in a zip archive into the system.
    """

    with ZipFile(zipfile, 'r', ZIP_STORED, True) as archive:
        for filename in archive.namelist():
            current_file = File.query.filter(File.file_hash == filename).filter(File.file_data == None).first()

            if current_file is None:
                continue

            current_file.file_data = archive.read(filename)

        try:
            DB.session.commit()
        except IntegrityError as err:
            print(err)
