#!/usr/bin/bash

SOURCE="/usr/src/Verleihsystem TTF"

NAME=total-tolles-ferleihsystem
PACKAGE=total_tolles_ferleihsystem

PYTHON=/usr/bin/python3
PIP_VENV="python -m pip"
VENV="virtualenv --python=$PYTHON"
NPM_BUILD_SCRIPT=production-build

LIB_PATH=/usr/lib/$NAME
LOG_PATH=/var/log/$NAME
APACHE_CONFIG_PATH=/etc/apache2

CONFIG_FILE=/etc/$NAME.conf
WSGI_FILE=/var/www/$NAME.wsgi
APACHE_CONFIG_FILE=$APACHE_CONFIG_PATH/sites-available/$NAME.conf


#
# --- Setup venv and activate it ---
#

# setup venv
if [ ! -d $LIB_PATH ]; then
    $VENV $LIB_PATH
fi

# activate venv
source $LIB_PATH/bin/activate

# install the ttf software and it's requirements into the venv
$PIP_VENV install -r requirements.txt
$PIP_VENV install -e .

# select web directory
pushd $PACKAGE

# build webpage
npm install -g node-gyp
npm install --unsafe-perm
npm run $NPM_BUILD_SCRIPT

# deselect directory
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

activate_this = '$LIB_PATH/bin/activate_this.py'
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

# deactivate venv
deactivate

# reload apache
service apache2 reload
