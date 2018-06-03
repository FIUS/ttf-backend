from .. import celery, APP

from . import TASK_LOGGER


@celery.task()
def sample(a, b):
    result = a + b
    TASK_LOGGER.info(result)
    return result
