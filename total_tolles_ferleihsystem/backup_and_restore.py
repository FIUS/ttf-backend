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
