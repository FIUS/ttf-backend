"""Module containing the root resource of the API."""

from flask_restplus import Resource
from . import api
from .models import root_model

ns = api.namespace('default', path='/')

@ns.route('/')
class RootResource(Resource):

    @ns.marshal_with(root_model)
    def get(self):
        return 'TODO'
