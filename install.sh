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
NPM_BUILD_SCRIPT=production-build

LOG_PATH=/var/log/$NAME
APACHE_CONFIG_PATH=/etc/apache2

CONFIG_FILE=/etc/$NAME.conf
WSGI_FILE=/var/www/$NAME.wsgi
APACHE_CONFIG_FILE=$APACHE_CONFIG_PATH/sites-available/$NAME.conf


if [ ! -d $VENV_DIR ]; then
    mkdir $VENV_DIR
fi

pushd $VENV_DIR

if [ ! -d $VENV_FOLDER ]; then
    $VENV $VENV_FOLDER
fi

pushd $VENV_FOLDER

chmod a+x bin/activate

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


#
# --- Create files and folders ---
#

# create log folder
mkdir -p $LOG_PATH


# create wsgi file
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


# create the ttf config file
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


# create the apache configuration file and activate it
if [ ! -f $APACHE_CONFIG_FILE ]; then
    echo "[INFO] Create apache2 config file: $APACHE_CONFIG_FILE"
    cat > $APACHE_CONFIG_FILE << EOF
<VirtualHost *:80>
    ServerName example.com
    WSGIDaemonProcess $NAME processes=2 threads=15
    WSGIProcessGroup $NAME
    WSGIScriptAlias / $WSGI_FILE
    WSGIPassAuthorization on
</VirtualHost>
EOF
    a2ensite ${NAME}
else
    echo "[WARN] Can't create apache2 config file: $APACHE_CONFIG_FILE; It already exists!"
fi


#
# --- Cleanup / Reload ---
#

# run db migrations
pushd $SOURCE
    MODE=production FLASK_APP=$PACKAGE flask db upgrade
popd

# reload apache
service apache2 reload
