from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required

from . import API, satisfies_role
from total_tolles_ferleihsystem.tasks.sample_task import sample

PATH: str = '/tasks'
ANS = API.namespace('tasks', description='Tasks', path=PATH)

@ANS.route('/')
class Taks(Resource):

    def get(self):
        from .. import celery
        registered = [task.name for task in celery.tasks.values()]
        inspect = celery.control.inspect
        i = inspect()
        running = [t for t in i.active()]
        return {'registered': registered, 'running': running}


@ANS.route('/test/')
class TestTaks(Resource):

    def post(self):
        sample.delay(1, 2)
        return 'task run'
