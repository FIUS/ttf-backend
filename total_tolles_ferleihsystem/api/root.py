"""
Module containing the root resource of the API.
"""

from flask_restplus import Resource
from flask_jwt_extended import jwt_optional
from . import API
from .models import ROOT_MODEL, CATALOG_MODEL

ANS = API.namespace('default', path='/')

@ANS.route('/')
class RootResource(Resource):
    """
    The API root element
    """

    @API.doc(security=None)
    @jwt_optional
    @API.marshal_with(ROOT_MODEL)
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

    @API.doc(security=None)
    @jwt_optional
    @API.marshal_with(CATALOG_MODEL)
    # pylint: disable=R0201
    def get(self):
        """
        Get the catalog element
        """
        return
