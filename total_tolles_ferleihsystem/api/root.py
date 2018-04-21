"""
Module containing the root resource of the API.
"""

from flask_restplus import Resource
from flask_jwt_extended import jwt_required, jwt_optional
from . import api
from .models import ROOT_MODEL, CATALOG_MODEL

ANS = api.namespace('default', path='/')

@ANS.route('/')
class RootResource(Resource):
    """
    The API root element
    """

    @jwt_optional
    @api.marshal_with(ROOT_MODEL)
    # pylint: disable=R0201
    def get(self):
        """
        Get the root element
        """
        return


@ANS.route('/catalog/')
class CatalogResource(Resource):
    """
    The catalog root element
    """

    @jwt_optional
    @api.marshal_with(CATALOG_MODEL)
    # pylint: disable=R0201
    def get(self):
        """
        Get the catalog element
        """
        return
