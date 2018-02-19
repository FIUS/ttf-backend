import click
from flask import Flask, logging
from logging import Logger, StreamHandler, Formatter
from sys import stdout


from .. import app, db

DB_COMMAND_LOGGER = logging.create_logger(app)  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)


@app.cli.command('create_db')
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    db.create_all()
    app.logger.info('Database created.')


@app.cli.command('drop_db')
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    db.drop_all()
    app.logger.info('Dropped Database.')
