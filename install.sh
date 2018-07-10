#!/usr/bin/bash

SOURCE="/usr/src/Verleihsystem TTF"
PACKAGE=total_tolles_ferleihsystem
NAME=total-tolles-ferleihsystem
PYTHON=/usr/bin/python3
PIP="$PYTHON -m pip"
PIP_VENV="python -m pip"
VENV="virtualenv --python=$PYTHON"
VENV_DIR=/usr/lib/
VENV_FOLDER=total-tolles-ferleihsystem
NPM_BUILD_SCRIPT=build-docker

CONFIG_FILE=/etc/${NAME}.conf
WSGI_FILE=/var/www/${NAME}.wsgi

LOG_PATH=/var/log/$NAME
APACHE_CONFIG_PATH=/etc/apache2

#Asset deploy url
DEPLOY_URL=./assets/

if [ ! -d $VENV_DIR ]; then
    mkdir $VENV_DIR
fi

pushd $VENV_DIR

if [ ! -d $VENV_FOLDER ]; then
    $VENV $VENV_FOLDER
fi

pushd $VENV_FOLDER

chmod a+x bin/activate*

source bin/activate

popd
popd


pushd $SOURCE

$PIP_VENV install -r requirements.txt

$PIP_VENV install -e .

pushd $PACKAGE

npm install -g node-gyp

npm install --unsafe-perm

if [ ! -d build ]; then
    mkdir build
fi

npm run $NPM_BUILD_SCRIPT

popd
popd


if [ ! -f $WSGI_FILE ]; then
    echo "[INFO] Create WSGI file: $WSGI_FILE"
    cat > $WSGI_FILE << EOF
import sys
from os import environ

activate_this = '$VENV_DIR$VENV_FOLDER/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '$SOURCE')
environ['MODE'] = 'production'
environ['JWT_SECRET_KEY'] = '$(hexdump -n 32 -e '4/4 "%08X" 1 ""' /dev/urandom)'

from $PACKAGE import APP as application
EOF
else
    echo "[WARN] Can't create WSGI file: $WSGI_FILE; It already exists!"
fi


if [ ! -f $CONFIG_FILE ]; then
    echo "[INFO] Create config file: $CONFIG_FILE"
    cat > $CONFIG_FILE << EOF
WEBPACK_MANIFEST_PATH = '$SOURCE/$PACKAGE/build/manifest.json'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/apache.db'
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://'
LOG_PATH = '$LOG_PATH'
EOF
else
    echo "[WARN] Can't create config file: $CONFIG_FILE; It already exists!"
fi


if [ ! -d $LOG_PATH ]; then
    mkdir $LOG_PATH
fi

pushd $APACHE_CONFIG_PATH

if [ ! -d sites-available ]; then
    mkdir sites-available
fi

pushd sites-available

if [ ! -f ${NAME}.conf ]; then
    echo "<VirtualHost *>" >> ${NAME}.conf
    echo "    ServerName example.com" >> ${NAME}.conf
    echo "    WSGIDaemonProcess $NAME processes=2 threads=15" >> ${NAME}.conf
    echo "    WSGIProcessGroup $NAME" >> ${NAME}.conf
    echo "    WSGIScriptAlias / $HTTP_ROOT/$WSGI_FILE" >> ${NAME}.conf
    echo "    WSGIPassAuthorization on" >> ${NAME}.conf
    echo "</VirtualHost>" >> ${NAME}.conf
fi

a2ensite ${NAME}

popd

popd

# run db migrations
pushd $SOURCE
    MODE=production FLASK_APP=$PACKAGE flask db upgrade
popd

# reload apache
touch $WSGI_FILE
