from celery import Celery
from logging import Logger, Formatter, DEBUG, INFO, getLogger
from logging.handlers import RotatingFileHandler
from os import path

from .. import APP

TASK_LOGGER: Logger = getLogger(APP.logger_name + '.tasks')


FORMATTER = Formatter(fmt=APP.config['LOG_FORMAT'])

FH = RotatingFileHandler(path.join(APP.config['LOG_PATH'], 'ttf_tasks.log'),
                         maxBytes=104857600, backupCount=10)

FH.setFormatter(FORMATTER)
FH.setLevel(INFO)

TASK_LOGGER.addHandler(FH)

TASK_LOGGER.setLevel(DEBUG)

def make_celery(app) -> Celery:
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    TASK_LOGGER.info('Initialized Celery with broker "%s" and result-store "%s"',
                     app.config['CELERY_BROKER_URL'],
                     app.config['CELERY_RESULT_BACKEND'])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            TASK_LOGGER.debug('Starting task %s', self.name)
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
