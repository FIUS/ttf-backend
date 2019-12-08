"""
TTF Module
"""
from sys import platform

from os import environ, path
from logging import getLogger, Logger
from logging.config import dictConfig

from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import MetaData
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_static_digest import FlaskStaticDigest
from flask_cors import CORS, cross_origin

FLASK_STATIC_DIGEST = FlaskStaticDigest()
# Setup Config

APP = Flask(__name__, instance_relative_config=True)  # type: Flask
APP.config['MODE'] = environ['MODE'].upper()
if APP.config['MODE'] == 'PRODUCTION':
    APP.config.from_object('total_tolles_ferleihsystem.config.ProductionConfig')
elif APP.config['MODE'] == 'DEBUG':
    APP.config.from_object('total_tolles_ferleihsystem.config.DebugConfig')
elif APP.config['MODE'] == 'TEST':
    APP.config.from_object('total_tolles_ferleihsystem.config.TestingConfig')

APP.config.from_pyfile('/etc/total-tolles-ferleihsystem.conf', silent=True)
APP.config.from_pyfile('total-tolles-ferleihsystem.conf', silent=True)
if ('CONFIG_FILE' in environ):
    APP.config.from_pyfile(environ.get('CONFIG_FILE', 'total-tolles-ferleihsystem.conf'), silent=True)

CONFIG_KEYS = ('SQLALCHEMY_DATABASE_URI', 'CELERY_BROKER_URL', 'CELERY_RESULT_BACKEND', 'JWT_SECRET_KEY')
for env_var in CONFIG_KEYS:
    APP.config[env_var] = environ.get(env_var, APP.config.get(env_var))

dictConfig(APP.config['LOGGING'])

APP.logger.debug('Debug logging enabled')
APP.logger.info('Connecting to database %s.', APP.config['SQLALCHEMY_DATABASE_URI'])

AUTH_LOGGER = getLogger('flask.app.auth')  # type: Logger
LENDING_LOGGER = getLogger('ttf.lending')  # type: Logger

# Setup DB with Migrations and bcrypt
DB: SQLAlchemy
DB = SQLAlchemy(APP, metadata=MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
}))

MIGRATE: Migrate = Migrate(APP, DB)
BCRYPT: Bcrypt = Bcrypt(APP)

# Setup JWT
JWT: JWTManager = JWTManager(APP)

# Setup Headers
CORS(APP)


FLASK_STATIC_DIGEST.init_app(APP)

# Setup Celery
# pylint: disable=C0413
from .tasks import make_celery
celery = make_celery(APP)

# Import LoginProviders
# pylint: disable=C0413
from . import auth_providers

# pylint: disable=C0413
from . import db_models
# pylint: disable=C0413
from . import routes
# pylint: disable=C0413
from . import backup_and_restore

# setup performance logging
if APP.config.get('MONITOR_REQUEST_PERFORMANCE', True):
    # pylint: disable=C0413
    from . import performance
