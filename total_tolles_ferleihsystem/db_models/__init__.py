import click
from flask import Flask, logging
from logging import Logger, StreamHandler, Formatter
from sys import stdout


from .. import APP, DB

DB_COMMAND_LOGGER = logging.create_logger(APP)  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)

STD_STRING_SIZE = 255


from . import blacklist, item, itemType, tag


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
