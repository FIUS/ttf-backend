"""Module containing default config values."""

from random import randint
import logging


class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    JWT_CLAIMS_IN_REFRESH_TOKEN = True
    JWT_SECRET_KEY = ''.join(hex(randint(0, 255))[2:] for i in range(16))
    CORS_ORIGINS = []
    CORS_SUPPORTS_CREDENTIALS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_UNIQUE_CONSTRAIN_FAIL = 'UNIQUE constraint failed'
    REVERSE_PROXY_COUNT = 0
    LOGGING = {
        'version': 1,
        'formatters': {
            'extended': {
                'format': '%(asctime)s [%(levelname)s] [%(name)-16s] %(message)s <%(module)s, \
                 %(funcName)s, %(lineno)s; %(pathname)s>',
            },
            'short': {
                'format': '[%(asctime)s] [%(levelname)s] [%(name)-16s] %(message)s',
            }
        },
        'handlers': {
            'default': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'extended',
                'filename': '/tmp/ttf-default.log',
                'maxBytes': 104857600,
                'backupCount': 10,
            },
            'auth': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'short',
                'filename': '/tmp/ttf-auth.log',
                'maxBytes': 104857600,
                'backupCount': 10,
            },
            'query': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'short',
                'filename': '/tmp/ttf-querys.log',
                'maxBytes': 104857600,
                'backupCount': 2,
            },
            'lending': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'short',
                'filename': '/tmp/ttf-lending.log',
                'maxBytes': 104857600,
                'backupCount': 100,
            },
            'performance': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'short',
                'filename': '/tmp/ttf-performance.log',
                'maxBytes': 104857600,
                'backupCount': 2,
            },
            'console': {
                'class' : 'logging.StreamHandler',
                'formatter': 'extended',
            }
        },
        'loggers': {
            'flask.app.auth': {
                'level': logging.INFO,
                'propagate': False,
                'handlers': ['auth'],
            },
            'flask.app.db': {
                'level': logging.WARNING,
                'propagate': False,
                'handlers': ['query'],
            },
            'sqlalchemy': {
                'level': logging.WARNING,
                'propagate': False,
                'handlers': ['query'],
            },
            'ttf.lending': {
                'level': logging.INFO,
                'propagate': False,
                'handlers': ['lending'],
            },
            'ttf.tasks': {
                'level': logging.WARNING,
                'propagate': False,
                'handlers': ['default'],
            },
            'ttf.performance': {
                'level': logging.WARNING,
                'propagate': False,
                'handlers': ['performance']
            }
        },
        'root': {
            'level': logging.WARNING,
            'handlers': ['default'],
        },
        'disable_existing_loggers': True,
    }
    CELERY_BROKER_URL = 'amqp://localhost',
    CELERY_RESULT_BACKEND = 'rpc://'
    TMP_DIRECTORY = '/tmp'
    DATA_DIRECTORY = '/tmp'

    LOGIN_PROVIDERS = ['Basic']

    BASIC_AUTH_ADMIN_PASS = ''.join(hex(randint(0, 255))[2:] for i in range(8))
    BASIC_AUTH_MOD_PASS = ''.join(hex(randint(0, 255))[2:] for i in range(8))

    LDAP_URI = ""
    LDAP_PORT = 0
    LDAP_SSL = False
    LDAP_START_TLS = False
    LDAP_USER_SEARCH_BASE = ""
    LDAP_GROUP_SEARCH_BASE = ""
    LDAP_USER_RDN = ""
    LDAP_USER_UID_FIELD = ""
    LDAP_GROUP_MEMBERSHIP_FIELD = ""
    LDAP_MODERATOR_FILTER = ""
    LDAP_ADMIN_FILTER = ""
    LDAP_MODERATOR_GROUP_FILTER = ""
    LDAP_ADMIN_GROUP_FILTER = ""

    MONITOR_REQUEST_PERORMANCE = True
    LONG_REQUEST_THRESHHOLD = 1

    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    RESTPLUS_JSON = {'indent': None}


class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    LONG_REQUEST_THRESHHOLD = 0
    JWT_SECRET_KEY = 'debug'
    JWT_ACCESS_TOKEN_EXPIRES = False
    CORS_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*"]
    LOGIN_PROVIDERS = ['Debug']
    Config.LOGGING['loggers']['flask.app.auth']['level'] = logging.DEBUG
    Config.LOGGING['loggers']['flask.app.db']['level'] = logging.DEBUG
    Config.LOGGING['loggers']['sqlalchemy.engine'] = {
        'level': logging.WARN,
        'propagate': False,
        'handlers': ['query'],
    }
    Config.LOGGING['loggers']['ttf.lending']['level'] = logging.DEBUG
    Config.LOGGING['loggers']['ttf.tasks']['level'] = logging.DEBUG
    Config.LOGGING['loggers']['ttf.performance']['level'] = logging.DEBUG
    Config.LOGGING['loggers']['flask.app.auth']['level'] = logging.DEBUG

    Config.LOGGING['root']['handlers'].append('console')
    Config.LOGGING['loggers']['ttf.performance']['handlers'].append('console')


class TestingConfig(Config):
    TESTING = True
