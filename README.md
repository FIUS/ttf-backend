# ttf-backend
The backend of the "Total Tolles Ferleihsystem" (our lending system).

TEST

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
This software can be deployed using docker or on a machine using our install script.

### Using Docker
A Dockerfile for the application is provided.
It is also published as a container under [fius/ttf-backend](https://hub.docker.com/r/fius/ttf-backend).
It uses different defaults for some config variables. For details see [docker](docker).
For the database Sqlite is used. The database is stored under `/app-mnt` within the container.
The binary files uploaded through the file api are also stored there.
Therefore, that folder is declared as a volume.
Additionally, the file `/app-mnt/total-tolles-ferleihsystem.conf` is read for any extra configuration.

A sperate Dockerfile and container are provided for the worker.
However, a broker is additionally required.

To properly run this software multiple containers with the different software components are advisable.
This can be achived by the following `docker-compose.yml`:
```yml
version: "3"

networks:
  ttf:
    external: false

services:
  rabbitmq:
    image: rabbitmq:3-alpine
    restart: always
    hostname: rabbitmq
    environment:
      TZ: Europe/Berlin
    networks:
      - ttf

  mariadb:
    image: mariadb:10
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: supersecret
      MYSQL_DATABASE: ttf
      MYSQL_USER: ttf
      MYSQL_PASSWORD: secret
      TZ: Europe/Berlin
    networks:
      - ttf

  ttf-backend:
    image: ttf-backend
    restart: always
    environment:
      CELERY_BROKER_URL: amqp://rabbitmq
      SQLALCHEMY_DATABASE_URI: mysql+cymysql://ttf:secret@mariadb:3306/ttf
      SWT_SECRET_KEY: megasecret
      TZ: Europe/Berlin
    ports:
      - "8088:80"
    depends_on:
      - rabbitmq
      - mariadb
    networks:
      - ttf

  ttf-worker:
    image: ttf-worker
    restart: always
    environment:
      CELERY_BROKER_URL: amqp://rabbitmq
      SQLALCHEMY_DATABASE_URI: mysql+cymysql://ttf:secret@mariadb:3306/ttf
      TZ: Europe/Berlin
    depends_on:
      - rabbitmq
      - mariadb
      - ttf-backend
    networks:
      - ttf

  ttf-scheduler:
    image: ttf-worker
    entrypoint: ["celery", "-A", "total_tolles_ferleihsystem", "beat", "-s", "/app-mnt/celerybeat-schedule"]
    restart: always
    environment:
      CELERY_BROKER_URL: amqp://rabbitmq
      SQLALCHEMY_DATABASE_URI: mysql+cymysql://ttf:secret@mariadb:3306/ttf
      TZ: Europe/Berlin
    depends_on:
      - rabbitmq
      - mariadb
      - ttf-backend
    networks:
      - ttf
```
Be sure the replace the secrets `secret` (at 4 positions), `supersecret` and `megasecret`.

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

### Reverseproxy
This project can run behind a reverse proxy with the help of [ProxyFix](https://werkzeug.palletsprojects.com/en/1.0.x/middleware/proxy_fix/). \
ProxyFix uses the headers set by the reverseproxy to adjust the wsgi environment accordingly. For more info visit their website. \
The number of trusted reverse proxies can be configured using the `REVERSE_PROXY_COUNT` config or environment variable.
