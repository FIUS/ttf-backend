"""
Collection of all backgroud workers who deal with files
"""

from typing import Tuple, List
from sqlalchemy.exc import IntegrityError
from .. import celery, DB
from ..file_store import create_archive as create_file_archive
from ..db_models.item import File

from . import TASK_LOGGER


Hash = str
# pylint: disable=C0103
FileEntry = Tuple[Hash, str]


@celery.task(name='ttf.tasks.file.create_archive')
def create_archive(archive_id: int, files: List[FileEntry]) -> None:
    """
    Task which creates a archive with the given parameters.
    """
    TASK_LOGGER.info(f'Start creating archive Nr. {archive_id} with {len(files)} Files.')
    file_hash = create_file_archive(files)
    TASK_LOGGER.info(f'Created Archive {archive_id}')
    file = File.query.filter(File.id == archive_id).first()
    file.file_hash = file_hash

    try:
        DB.session.commit()
        TASK_LOGGER.info(f'Success on archive {archive_id}')
    except IntegrityError as err:
        TASK_LOGGER.error('Error occured: %s', str(err))
