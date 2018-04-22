from os import environ, path
from logging import Formatter
from logging.handlers import RotatingFileHandler

from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_webpack import Webpack
from flask_cors import CORS, cross_origin


webpack = Webpack()  # type: Webpack


# Setup Config

app = Flask(__name__, instance_relative_config=True)  # type: Flask
app.config['MODE'] = environ['MODE'].upper()
if app.config['MODE'] == 'PRODUCTION':
    app.config.from_object('total_tolles_ferleihsystem.config.ProductionConfig')
elif app.config['MODE'] == 'DEBUG':
    app.config.from_object('total_tolles_ferleihsystem.config.DebugConfig')
elif app.config['MODE'] == 'TEST':
    app.config.from_object('total_tolles_ferleihsystem.config.TestingConfig')

app.config.from_pyfile('total_tolles_ferleihsystem.conf', silent=True)

# TODO use nevironment variables


formatter = Formatter(fmt=app.config['LOG_FORMAT'])

fh = RotatingFileHandler(path.join(app.config['LOG_PATH'], 'ttf.log'),
                         maxBytes=104857600, backupCount=10)

fh.setFormatter(formatter)

app.logger.addHandler(fh)

app.logger.info('Connecting to database %s.', app.config['SQLALCHEMY_DATABASE_URI'])


# Setup DB and bcrypt
db = SQLAlchemy(app)  # type: SQLAlchemy
bcrypt = Bcrypt(app)  # type: Bcrypt

# Setup JWT
JWT = JWTManager(app)  # type: JWTManager

# Setup Headers
CORS(app)


webpack.init_app(app)


from . import db_models

from . import routes
