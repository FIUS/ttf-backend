# Documentation of all config options

Options are read from the following sources. Options in later sources overwrite previous options.

 1. Defaults from `config.py` module.
 2. `/etc/total-tolles-ferleihsystem.conf`
 3. `./total-tolles-ferleihsystem.conf`
 4. Path specified in `CONFIG_FILE`
 5. Environment Variables


## Main options:

| name                    | ENV                | description | standard value |
|:------------------------|:------------------:|:------------|:--------------:|
| FLASK_APP               | :heavy_check_mark: | Name of Flask APP | `total_tolles_ferleihsystem` |
| MODE                    | :heavy_check_mark: | Mode Selector for `PRODUCTION`, `DEBUG` or `TEST` Environment. Only as env variable! | `PRODUCTION` |
| JWT_SECRET_KEY          | :heavy_check_mark: | Secret key for JWT Tokens. Do NOT make this public! Use a random string! |  |
| SQLALCHEMY_DATABASE_URI | :heavy_check_mark: | Url for Database. [More Info](README.md#install) | `sqlite://:memory:` |
| SQLITE_FOREIGN_KEYS     |                    | Use Sqlite with Foreign Key checks enabled.  | `True` |
| WEBPACK_MANIFEST_PATH   |                    | Path to Manifest.json written by npm build. | `./build/manifest.json` |
| LOG_PATH                | :heavy_check_mark: | Path to log folder. | `/tmp` |
| TMP_DIRECTORY           |                    | | `/tmp` |
| DATA_DIRECTORY          |                    | | `/tmp` |
| CONFIG_FILE             | :heavy_check_mark: | Path to a valid config file (python file). Only as env variable!| `total-tolles-ferleihsystem.conf` |
| CELERY_BROKER_URL       | :heavy_check_mark: | Url for Celery compatible Broker. [More Info](README.md#install) | `amqp://localhost` |
| CELERY_RESULT_BACKEND   | :heavy_check_mark: | Url for Celery compatible result Backend. [More Info](README.md#install) | `rpc://` |
| LOG_FORMAT              |                    | Standard Python log format string. |  |
| AUTH_LOG_FORMAT         |                    | Standard Python log format string. |  |


## Third party options:

 *  [Flask options](http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values)
 *  [FlaskSQLAlchemy options](http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys)
 *  [Flask JWT-Extended options](https://flask-jwt-extended.readthedocs.io/en/latest/options.html)
 *  [Flask Restplus options](https://flask-restplus.readthedocs.io/en/latest/swagger.html?highlight=RESTPLUS_VALIDATE#the-api-expect-decorator)
 *  [Celery options](http://docs.celeryproject.org/en/latest/userguide/configuration.html)
