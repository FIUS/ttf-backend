import sys

from invoke import task, context
from os import environ
from shutil import rmtree
from pathlib import Path
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from inspect import getmembers, isclass
from total_tolles_ferleihsystem.db_models import DB
from total_tolles_ferleihsystem.db_models import attributeDefinition, blacklist, item, itemType, ruleEngine, settings, tag


SHELL = environ.get('SHELL', 'bash')

BUILD_FOLDER = Path('./total_tolles_ferleihsystem/build')
MANIFEST_PATH = BUILD_FOLDER / Path('manifest.json')


@task
def clean_js_dependencies(c):
    print('Removing node_modules folder.')
    rmtree(Path('./total_tolles_ferleihsystem/node_modules'))


@task
def dependencies_py(c, production=False):
    if production:
        c.run('pipenv install --deploy', shell=SHELL)
    else:
        c.run('pipenv install', shell=SHELL)


@task
def dependencies_js(c, clean_dependencies=False):
    if clean_dependencies:
        clean_js_dependencies(c)
    with c.cd('./total_tolles_ferleihsystem'):
        c.run('npm install', shell=SHELL)


@task(dependencies_py, dependencies_js)
def dependencies(c):
    pass


@task(dependencies_js)
def build(c):
    if not BUILD_FOLDER.exists():
        BUILD_FOLDER.mkdir()
    with c.cd('./total_tolles_ferleihsystem'):
        c.run('npm run build', shell=SHELL)


@task
def start_js(c):
    with c.cd('./total_tolles_ferleihsystem'):
        c.run('npm run start', shell=SHELL, pty=True)


@task
def start_py(c):
    # check manifest.json path:
    if not (MANIFEST_PATH.exists() and MANIFEST_PATH.is_file()):
        build(c)
    c.run('flask run', shell=SHELL, pty=True)


@task
def sql_schema(c, dialect="mysql"):
    sql_dialect: any
    if dialect == "mysql":
        sql_dialect = mysql.dialect()

    tables: dict(str, any) = {}

    for file in [attributeDefinition, blacklist, item, itemType, ruleEngine, settings, tag]:
        for name, member in getmembers(sys.modules[file.__name__], isclass):
            if issubclass(member, DB.Model):
                if not name in tables:
                    tables[name] = member

    for table in tables:
        print(str(CreateTable(tables[table].__table__).compile(dialect=sql_dialect)) + ";")
