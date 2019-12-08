from flask import render_template, url_for, send_from_directory, redirect
#from flask_static_digest import static_url_for
from flask_cors import CORS, cross_origin

from . import APP, FLASK_STATIC_DIGEST

from . import api

from .db_models import STD_STRING_SIZE

if APP.config.get('DEBUG', False):
    from . import debug_routes


@APP.route('/', defaults={'path': ''})
@APP.route('/<path:path>')
def index(path):
    base_path = APP.config.get('APPLICATION_ROOT', '/')
    if base_path is None:
        base_path = '/'
    api_base_path = url_for('api.default_root_resource')
    return render_template('index.html',
                           title='Total Tolles Ferleihsystem',
                           angularBasePath=base_path,
                           apiBasePath=api_base_path,
                           maxDBStringLength=STD_STRING_SIZE)



@APP.route('/<string:file>')
def asset(file):
    if '.' in file:
        return redirect(FLASK_STATIC_DIGEST.static_url_for('static', filename=file))
    base_path = APP.config.get('APPLICATION_ROOT', '/')
    if base_path is None:
        base_path = '/'
    api_base_path = url_for('api.default_root_resource')
    return render_template('index.html',
                           title='Total Tolles Ferleihsystem',
                           angularBasePath=base_path,
                           apiBasePath=api_base_path,
                           maxDBStringLength=STD_STRING_SIZE)
