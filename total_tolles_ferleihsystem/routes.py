from flask import render_template, url_for, send_from_directory, redirect
#from flask_static_digest import static_url_for
from flask_cors import CORS, cross_origin

from . import APP

from . import api

if APP.config.get('DEBUG', False):
    from . import debug_routes
