from flask import render_template, url_for, send_from_directory
from flask_cors import CORS, cross_origin

from . import APP

from . import api

from .db_models import STD_STRING_SIZE

if APP.config['DEBUG']:
    from . import debug_routes


@APP.route('/')
@APP.route('/index')
def index():
    return render_template('index.html',
                           title='Total Tolles Ferleihsystem',
                           maxDBStringLength=STD_STRING_SIZE)


@APP.route('/assets/<path:file>')
def asset(file):
    return send_from_directory('./build', file)
