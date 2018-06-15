from flask import render_template, url_for, send_from_directory
from flask_cors import CORS, cross_origin

from . import APP

from . import api

if APP.config['DEBUG']:
    from . import debug_routes


@APP.route('/')
@APP.route('/index')
def index():
    return render_template('index.html',
                           title='Total Tolles Ferleihsystem')


@APP.route('/assets/<path:file>')
def asset(file):
    return send_from_directory('./build', file)
