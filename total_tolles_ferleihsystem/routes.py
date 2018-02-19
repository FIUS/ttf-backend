from flask import render_template, url_for
from flask_cors import CORS, cross_origin

from . import app

from . import api

if app.config['DEBUG']:
    from . import debug_routes


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Total Tolles Ferleihsystem')
