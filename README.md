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


## Update DB Migrations:

The migrations use [Flask-Migrate](flask-migrate.readthedocs.io/en/latest/).

Commands:
```shell
# create new migration after model changes:
flask db migrate

# update db to newest migration:
flask db upgrade

# get help for db operations:
flask db --help
```

After creating a new migration file with `flask db migrate` it is neccessary to manually check the generated upgrade script. Please refer to the [alembic documentation](alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).


## Install:

Prerequisites:

 *  Python >3.6, Virtualenv, Pip
 *  npm, node >8
 *  Apache2, mod-wsgi
 *  Celery Broker (documentation)[http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html]
 *  Celery Scheduler celery scheduler for recurring tasks (documentation)[http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html]

Installation / Upgrade process:

 1. Install Prerequisites
 2. Download/Clone Repository
 3. Copy `install.sh` to a different location outside of the repository
     1. Make it executable
     2. update the variables at the top of the script
 4. execute `install.sh`
 5. (Re-) Start Celery workers and scheduler

For use with MySql or other db engine:

 1. Setup Database User and scheme
     1. For MySql/Mariadb use [utf8mb4 charset](dev.mysql.com/doc/refman/5.5/en/charset-unicode-utf8mb4.html)
 2. Install a [driver](docs.sqlalchemy.org/en/latest/dialects/mysql.html) for your selected Database in the virtualenv
 3. Update the [database url](docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) in the config file
     1. For MySql/Mariadb use [utf8mb4 charset](docs.sqlalchemy.org/en/latest/dialects/mysql.html?highlight=utf8mb4#charset-selection)
 4. execute `install.sh` to generate database

Troubleshooting:

 *  Check all file permissions (use `install.sh` as reference)
 *  Check AppArmor/Selinux permissions
 *  Check apache logs
 *  Check apache config
 *  Check TTF logs
 *  Check Python version (>3.6!)
 *  Check if Celery Broker is running
 *  Check if workers are running
 *  Check if Celery Scheduler is running
