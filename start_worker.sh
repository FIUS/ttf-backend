#!/bin/bash

. venv/bin/activate
export FLASK_APP=total_tolles_ferleihsystem
export MODE=debug

# start celery worker (needs new terminal) with beats (only for debugging!)
celery -A total_tolles_ferleihsystem.celery worker -B --loglevel=info
