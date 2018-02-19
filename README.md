# TTF


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
npm build
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

