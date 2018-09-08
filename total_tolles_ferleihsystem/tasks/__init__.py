from celery import Celery
from logging import Logger, Formatter, DEBUG, INFO, getLogger
from logging.handlers import RotatingFileHandler
from os import path

from .. import APP

TASK_LOGGER: Logger = getLogger('flask.app.tasks')


FORMATTER = Formatter(fmt=APP.config['LOG_FORMAT'])

FH = RotatingFileHandler(path.join(APP.config['LOG_PATH'], 'ttf_tasks.log'),
                         maxBytes=104857600, backupCount=10)

FH.setFormatter(FORMATTER)
FH.setLevel(INFO)

TASK_LOGGER.addHandler(FH)

TASK_LOGGER.setLevel(DEBUG)


# http://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings
# Missing keys for automatic conversion:
# [...]_DB_SHORT_LIVED_SESSIONS: database_short_lived_sessions
# CELERY_RESULT_DBURI: Use result_backend instead.
CELERY_CONFIG_KEY_MAPPING = {
    'CELERY_ACCEPT_CONTENT': 'accept_content',
    'CELERY_ENABLE_UTC': 'enable_utc',
    'CELERY_IMPORTS': 'imports',
    'CELERY_INCLUDE': 'include',
    'CELERY_TIMEZONE': 'timezone',
    'CELERYBEAT_MAX_LOOP_INTERVAL': 'beat_max_loop_interval',
    'CELERYBEAT_SCHEDULE': 'beat_schedule',
    'CELERYBEAT_SCHEDULER': 'beat_scheduler',
    'CELERYBEAT_SCHEDULE_FILENAME': 'beat_schedule_filename',
    'CELERYBEAT_SYNC_EVERY': 'beat_sync_every',
    'BROKER_URL': 'broker_url',
    'BROKER_TRANSPORT': 'broker_transport',
    'BROKER_TRANSPORT_OPTIONS': 'broker_transport_options',
    'BROKER_CONNECTION_TIMEOUT': 'broker_connection_timeout',
    'BROKER_CONNECTION_RETRY': 'broker_connection_retry',
    'BROKER_CONNECTION_MAX_RETRIES': 'broker_connection_max_retries',
    'BROKER_FAILOVER_STRATEGY': 'broker_failover_strategy',
    'BROKER_HEARTBEAT': 'broker_heartbeat',
    'BROKER_LOGIN_METHOD': 'broker_login_method',
    'BROKER_POOL_LIMIT': 'broker_pool_limit',
    'BROKER_USE_SSL': 'broker_use_ssl',
    'CELERY_CACHE_BACKEND': 'cache_backend',
    'CELERY_CACHE_BACKEND_OPTIONS': 'cache_backend_options',
    'CASSANDRA_COLUMN_FAMILY': 'cassandra_table',
    'CASSANDRA_ENTRY_TTL': 'cassandra_entry_ttl',
    'CASSANDRA_KEYSPACE': 'cassandra_keyspace',
    'CASSANDRA_PORT': 'cassandra_port',
    'CASSANDRA_READ_CONSISTENCY': 'cassandra_read_consistency',
    'CASSANDRA_SERVERS': 'cassandra_servers',
    'CASSANDRA_WRITE_CONSISTENCY': 'cassandra_write_consistency',
    'CELERY_COUCHBASE_BACKEND_SETTINGS': 'couchbase_backend_settings',
    'CELERY_MONGODB_BACKEND_SETTINGS': 'mongodb_backend_settings',
    'CELERY_EVENT_QUEUE_EXPIRES': 'event_queue_expires',
    'CELERY_EVENT_QUEUE_TTL': 'event_queue_ttl',
    'CELERY_EVENT_QUEUE_PREFIX': 'event_queue_prefix',
    'CELERY_EVENT_SERIALIZER': 'event_serializer',
    'CELERY_REDIS_DB': 'redis_db',
    'CELERY_REDIS_HOST': 'redis_host',
    'CELERY_REDIS_MAX_CONNECTIONS': 'redis_max_connections',
    'CELERY_REDIS_PASSWORD': 'redis_password',
    'CELERY_REDIS_PORT': 'redis_port',
    'CELERY_RESULT_BACKEND': 'result_backend',
    'CELERY_MAX_CACHED_RESULTS': 'result_cache_max',
    'CELERY_MESSAGE_COMPRESSION': 'result_compression',
    'CELERY_RESULT_EXCHANGE': 'result_exchange',
    'CELERY_RESULT_EXCHANGE_TYPE': 'result_exchange_type',
    'CELERY_TASK_RESULT_EXPIRES': 'result_expires',
    'CELERY_RESULT_PERSISTENT': 'result_persistent',
    'CELERY_RESULT_SERIALIZER': 'result_serializer',
    'CELERY_RESULT_ENGINE_OPTIONS': 'database_engine_options',
    'CELERY_RESULT_DB_TABLE_NAMES': 'database_db_names',
    'CELERY_SECURITY_CERTIFICATE': 'security_certificate',
    'CELERY_SECURITY_CERT_STORE': 'security_cert_store',
    'CELERY_SECURITY_KEY': 'security_key',
    'CELERY_TASK_ACKS_LATE': 'task_acks_late',
    'CELERY_TASK_ALWAYS_EAGER': 'task_always_eager',
    'CELERY_TASK_ANNOTATIONS': 'task_annotations',
    'CELERY_TASK_COMPRESSION': 'task_compression',
    'CELERY_TASK_CREATE_MISSING_QUEUES': 'task_create_missing_queues',
    'CELERY_TASK_DEFAULT_DELIVERY_MODE': 'task_default_delivery_mode',
    'CELERY_TASK_DEFAULT_EXCHANGE': 'task_default_exchange',
    'CELERY_TASK_DEFAULT_EXCHANGE_TYPE': 'task_default_exchange_type',
    'CELERY_TASK_DEFAULT_QUEUE': 'task_default_queue',
    'CELERY_TASK_DEFAULT_RATE_LIMIT': 'task_default_rate_limit',
    'CELERY_TASK_DEFAULT_ROUTING_KEY': 'task_default_routing_key',
    'CELERY_TASK_EAGER_PROPAGATES': 'task_eager_propagates',
    'CELERY_TASK_IGNORE_RESULT': 'task_ignore_result',
    'CELERY_TASK_PUBLISH_RETRY': 'task_publish_retry',
    'CELERY_TASK_PUBLISH_RETRY_POLICY': 'task_publish_retry_policy',
    'CELERY_TASK_QUEUES': 'task_queues',
    'CELERY_TASK_ROUTES': 'task_routes',
    'CELERY_TASK_SEND_SENT_EVENT': 'task_send_sent_event',
    'CELERY_TASK_SERIALIZER': 'task_serializer',
    'CELERYD_TASK_SOFT_TIME_LIMIT': 'task_soft_time_limit',
    'CELERYD_TASK_TIME_LIMIT': 'task_time_limit',
    'CELERY_TRACK_STARTED': 'task_track_started',
    'CELERYD_AGENT': 'worker_agent',
    'CELERYD_AUTOSCALER': 'worker_autoscaler',
    'CELERYD_CONCURRENCY': 'worker_concurrency',
    'CELERYD_CONSUMER': 'worker_consumer',
    'CELERY_WORKER_DIRECT': 'worker_direct',
    'CELERY_DISABLE_RATE_LIMITS': 'worker_disable_rate_limits',
    'CELERY_ENABLE_REMOTE_CONTROL': 'worker_enable_remote_control',
    'CELERYD_HIJACK_ROOT_LOGGER': 'worker_hijack_root_logger',
    'CELERYD_LOG_COLOR': 'worker_log_color',
    'CELERYD_LOG_FORMAT': 'worker_log_format',
    'CELERYD_WORKER_LOST_WAIT': 'worker_lost_wait',
    'CELERYD_MAX_TASKS_PER_CHILD': 'worker_max_tasks_per_child',
    'CELERYD_POOL': 'worker_pool',
    'CELERYD_POOL_PUTLOCKS': 'worker_pool_putlocks',
    'CELERYD_POOL_RESTARTS': 'worker_pool_restarts',
    'CELERYD_PREFETCH_MULTIPLIER': 'worker_prefetch_multiplier',
    'CELERYD_REDIRECT_STDOUTS': 'worker_redirect_stdouts',
    'CELERYD_REDIRECT_STDOUTS_LEVEL': 'worker_redirect_stdouts_level',
    'CELERYD_SEND_EVENTS': 'worker_send_task_events',
    'CELERYD_STATE_DB': 'worker_state_db',
    'CELERYD_TASK_LOG_FORMAT': 'worker_task_log_format',
    'CELERYD_TIMER': 'worker_timer',
    'CELERYD_TIMER_PRECISION': 'worker_timer_precision',
}


def make_celery(app) -> Celery:
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery_config = {CELERY_CONFIG_KEY_MAPPING.get(key, key): value for key, value in app.config.items()}
    celery.conf.update(celery_config)

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
