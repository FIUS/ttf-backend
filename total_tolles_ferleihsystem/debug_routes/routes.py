import urllib
from flask import render_template, url_for
from .. import app
from . import debug_blueprint
"""Module containing debug routes index page."""


@debug_blueprint.route('/routes/')
def routes():
    output = []
    for rule in app.url_map.iter_rules():

        line = {
            'endpoint': rule.endpoint,
            'methods': ', '.join(rule.methods),
            'url': rule.rule
        }
        output.append(line)
    output.sort(key=lambda x: x['url'])
    return render_template('debug/routes/all.html',
                           title='Total Tolles Ferleihsystem – Routes',
                           routes=output)
