#!/bin/bash

. venv/bin/activate
export FLASK_APP=total_tolles_ferleihsystem
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug

# create debug db:
flask create_db

# start server
flask run
