"""Module containing default config values."""

from random import randint


class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    JWT_SECRET_KEY = ''.join(hex(randint(0, 255))[2:] for i in range(16))
    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = './build/manifest.json'
    LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)-16s] %(message)s <%(module)s, \
                 %(funcName)s, %(lineno)s; %(pathname)s>'
    AUTH_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    CELERY_BROKER_URL = 'amqp://localhost',
    CELERY_RESULT_BACKEND = 'rpc://'
    TMP_DIRECTORY = '/tmp'
    DATA_DIRECTORY = '/tmp'


class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    LOG_PATH = '/tmp'
    SQLALCHEMY_ECHO = True
    JWT_SECRET_KEY = 'debug'


class TestingConfig(Config):
    TESTING = True
    LOG_PATH = '/tmp'
