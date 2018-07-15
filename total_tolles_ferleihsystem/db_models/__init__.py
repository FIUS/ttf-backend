import click
from flask import Flask, logging
from logging import Logger, StreamHandler, Formatter, getLogger, DEBUG
from sys import stdout
from sqlalchemy.engine import Engine
from sqlalchemy import event


from .. import APP, DB

DB_COMMAND_LOGGER = getLogger(APP.logger_name + '.db')  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)

DB_COMMAND_LOGGER.setLevel(DEBUG)

STD_STRING_SIZE = 190  # Max size that allows Indices while using utf8mb4 in MySql DB


from . import attributeDefinition, blacklist, item, itemType, tag


if APP.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite://'):
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if APP.config.get('SQLITE_FOREIGN_KEYS', True):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


@APP.cli.command('create_db')
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    DB.create_all()
    APP.logger.info('Database created.')


@APP.cli.command('drop_db')
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    DB.drop_all()
    APP.logger.info('Dropped Database.')
