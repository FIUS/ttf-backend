"""
This module contains all API endpoints for the namespace 'file'
"""

from flask_restplus import Resource

from .. import API

PATH: str = '/catalog/files'
ANS = API.namespace('file', description='The file Endpoints', path=PATH)


@ANS.route('/')
class FileList(Resource):
    """
    Files root element
    """

    def get(self):
        """
        Get a list of files
        """
        pass

    def post(self):
        """
        Create a file
        """
        pass


@ANS.route('/<int:file_id>/')
class FileDetail(Resource):
    """
    Single file object
    """

    def get(self, file_id):
        """
        Get a single file object
        """
        pass

    def delete(self, file_id):
        """
        Delete a file object
        """
        pass

    def put(self, file_id):
        """
        Replace a file object
        """
        pass
