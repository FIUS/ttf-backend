from datetime import datetime
from celery.schedules import crontab
from .. import celery, APP

from . import TASK_LOGGER


@celery.task(name='ttf.tasks.sample_tasks.sample')
def sample(a, b):
    result = a + b
    TASK_LOGGER.info(result)
    return result

@celery.task(name='ttf.tasks.sample_tasks.recurring')
def recurring():
    TASK_LOGGER.info('Recurring Task executed at %s', datetime.now())


celery.conf.beat_schedule = {
    'execute-recurring': {
        'task': 'ttf.tasks.sample_tasks.recurring',
        'schedule': crontab(minute='*/5')
    }
}
