# ttf-backend
The backend of the "Total Tolles Ferleihsystem" (our lending system).

## Prerequesits
- python >= 3.6
- Pipenv [python >= 3.6]
- celery compatible Broker [documentation](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html)
- celery scheduler for recurring tasks [documentation](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)


## First start:
After you've cloned this repo you have to do some things to prepare for starting the project in your development environment:

First, you to set the environment variables required for starting.
For this the file `.env` in the root of the repo needs to be created and filled with the following:
```
FLASK_APP=total_tolles_ferleihsystem
FLASK_DEBUG=1  # to enable autoreload 
MODE=debug # or production or test
```

Then install the requirements including the development dependencies:
```shell
pipenv install --dev
```

## Starting development server:
First, create the db:
```shell
pipenv run upgrade-db
```

To start the server:
```shell
pipenv run start
```

To start a celery worker for background tasks (need running broker for this to work):
```shell
pipenv run start-celery-worker
```

To drop and recreate the database:
```shell
pipenv run drop-db
pipenv run upgrade-db
```

## Sites:

The following sites are available after starting the flask development server:

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


## Install for production:

### Using our install script

Prerequisites:

 *  Python >=3.6, Virtualenv, Pip
 *  Apache2, mod-wsgi
 *  Celery Broker [documentation](http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html)
 *  Celery Scheduler celery scheduler for recurring tasks [documentation](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)

Installation / Upgrade process:

 1. Install Prerequisites
 2. Download/Clone Repository
 3. Copy `install.sh` to a different location outside of the repository
     1. Make it executable
     2. update the variables at the top of the script
 4. execute `install.sh`
 5. check options: [documentation](options.md)
 6. (Re-) Start Celery workers and scheduler

For use with MySql or other db engine:

 1. Setup Database User and scheme
     1. For MySql/Mariadb use [utf8mb4 charset](http://dev.mysql.com/doc/refman/5.5/en/charset-unicode-utf8mb4.html)
 2. Install a [driver](http://docs.sqlalchemy.org/en/latest/dialects/mysql.html) for your selected Database in the virtualenv
 3. Update the [database url](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) in the config file
     1. For MySql/Mariadb use [utf8mb4 charset](http://docs.sqlalchemy.org/en/latest/dialects/mysql.html?highlight=utf8mb4#charset-selection)
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
