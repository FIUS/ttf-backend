from flask_restplus import Resource
from . import api

PATH: str = '/search'
ANS = api.namespace('search', description='The search resource', path=PATH)

@ANS.route('/')
class Search(Resource):
    """
    Search Resource
    """
    @api.doc(security=None)
    def get(self):
        return "Search Result"
