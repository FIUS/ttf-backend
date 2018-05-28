# TTF


## Prerequesits
- nodejs >8.0.0
- npm
- python 3.6
- pip [python 3.6]
- venv [python 3.6]
- celery compatible Broker (documentation)[http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html]

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

# start celery worker (needs new terminal)
celery -A total_tolles_ferleihsystem.celery worker --loglevel=info
```

Subsequent starts:
```shell
flask run
```

Drop and recreate DB:
```shell
flask drop_dbcelery -A total_tolles_ferleihsystem.celery worker --loglevel=info
flask create_db
```



## Sites:

The following sites are available after starting the flask development server:

[Web-App](http://127.0.0.1:5000/)
[API](http://127.0.0.1:5000/api/doc)

Only in debug mode:
[debug](http://127.0.0.1:5000/debug)
