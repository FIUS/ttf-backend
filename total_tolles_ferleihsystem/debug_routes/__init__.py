"""
Module containing Debug Methods and sites.

This Module should only be loaded in debug Mode.
"""

from flask import Blueprint, render_template
from .. import app

if not app.config['DEBUG']:
    raise ImportWarning("This Module should only be loaded if DEBUG mode is active!")

debug_blueprint = Blueprint('debug_routes', __name__, template_folder='templates',
                            static_folder='static')

from . import routes, debug_db_models


@debug_blueprint.route('/')
@debug_blueprint.route('/index')
def index():
    return render_template('debug/index.html',
                           title='Total Tolles Ferleihsystem – Debug')


app.register_blueprint(debug_blueprint, url_prefix='/debug')
