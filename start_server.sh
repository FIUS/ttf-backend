#!/bin/bash

. venv/bin/activate
export FLASK_APP=total_tolles_ferleihsystem
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug

# create debug db:
#flask db upgrade
flask db migrate

# start server
#flask run
