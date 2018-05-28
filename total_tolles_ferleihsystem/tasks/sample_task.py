from .. import celery, APP


@celery.task()
def sample(a, b):
    result = a + b
    APP.logger.info(result)
    return result
