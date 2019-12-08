from invoke import task, context
from os import environ
from shutil import rmtree
from pathlib import Path


SHELL = environ.get('SHELL', 'bash')

BUILD_FOLDER = Path('./total_tolles_ferleihsystem/static')


@task
def clean(c):
    print('Removing ui build output.')
    if BUILD_FOLDER.exists():
        rmtree(BUILD_FOLDER)


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
def build(c, production=False, deploy_url='/static/', base_href='/', clean_build=False):
    if clean_build:
        clean(c)
    if not BUILD_FOLDER.exists():
        BUILD_FOLDER.mkdir()
    c.run('flask digest clean', shell=SHELL)
    with c.cd('./total_tolles_ferleihsystem'):
        attrs = [
            '--',
            '--extract-css',
            "--deploy-url='{}'".format(deploy_url),
            "--base-href='{}'".format(base_href),
        ]
        if production:
            attrs.append('--prod')
        c.run('npm run build ' + ' '.join(attrs), shell=SHELL)
    c.run('flask digest compile', shell=SHELL)


@task
def start_js(c, deploy_url='/static/'):
    with c.cd('./total_tolles_ferleihsystem'):
        attrs = [
            '--',
            '--extract-css',
            "--deploy-url='{}'".format(deploy_url),
            "--watch",
        ]
        c.run('npm run build ' + ' '.join(attrs), shell=SHELL, pty=True)


@task
def start_py(c, autoreload=False):
    if autoreload:
        c.run('FLASK_DEBUG=1 flask run', shell=SHELL, pty=True)
    else:
        c.run('flask run', shell=SHELL, pty=True)
