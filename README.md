# TTF


## Prerequesits
- nodejs >8.0.0
- npm
- python 3.6
- pip [python 3.6]
- venv [python 3.6]
- celery compatible Broker (documentation)[http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html]
- celery scheduler for recurring tasks (documentation)[http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html]

## First start:

After you've cloned this repo you have to do the install routine for both backend AND frontend before starting the backend!

Backend:
```shell
# setup virtualenv
virtualenv venv
. venv/bin/activate


# install requirements
pip install -r requirements_developement.txt
pip install -r requirements.txt

pip install -e .
```

Frontend:

```shell
cd total_tolles_ferleihsystem

npm install
npm run build
```


## start server:

Start the webpack developement server:
```shell
cd total_tolles_ferleihsystem
npm run start
```

First start:
```shell
. venv/bin/activate
export FLASK_APP=total_tolles_ferleihsystem
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug
# export MODE=production
# export MODE=test

# create and init debug db:
flask create_db

# start server
flask run

# start celery worker (needs new terminal) with beats (only for debugging!)
celery -A total_tolles_ferleihsystem.celery worker -B --loglevel=info

## start celery worker for production:
# celery -A total_tolles_ferleihsystem.celery worker
## startcelery scheduler (beats) for production (needed for periodic tasks):
# celery -A total_tolles_ferleihsystem.celery beat -s <path to persitence db>
```

Subsequent starts:
```shell
flask run
```

Drop and recreate DB:
```shell
flask drop_db
flask create_db
```



## Sites:

The following sites are available after starting the flask development server:

[Web-App](http://127.0.0.1:5000/)
[API](http://127.0.0.1:5000/api/doc)

Only in debug mode:
[debug](http://127.0.0.1:5000/debug)
