"""
This module contains all API endpoints for the namespace 'file'
"""

import os
from flask import request
from flask_restplus import Resource, abort
from werkzeug.utils import secure_filename

from .. import API, APP


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
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        if file:
            if file.filename == '':
                abort(400)
            filename = secure_filename(file.filename)
            file.save(os.path.join(APP.config['DATA_DIRECTORY'], filename))
            return 'Success'


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


PATH2: str = '/file-store'
ANS2 = API.namespace('file', description='The download Endpoints to get the actual stored files', path=PATH)

@ANS2.route('/<string:hash>/')
class FileData(Resource):
    """
    The endpoints to get the actual stored file
    """

    def get(self, hash):
        """
        Get the actual file
        """
        pass
