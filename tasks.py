from invoke import task, context
from os import environ
from shutil import rmtree
from pathlib import Path


SHELL = environ.get('SHELL', 'bash')

BUILD_FOLDER = Path('./total_tolles_ferleihsystem/static')


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
    c.run('flask run', shell=SHELL, pty=True)
