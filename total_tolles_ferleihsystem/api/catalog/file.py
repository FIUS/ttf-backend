"""
This module contains all API endpoints for the namespace 'file'
"""

import os
import hashlib
from flask import request
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError

from ..models import FILE_GET
from ...db_models.item import Item, File

from .. import API, APP
from ... import DB

TMP_FILE_NAME = 'tmp.upload'


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

    @API.marshal_with(FILE_GET)
    def post(self):
        """
        Create a file
        """
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        if not file:
            abort(400)
        if file.filename == '':
            abort(400)
        if request.form['item_id'] is None:
            abort(400)
        if Item.query.filter(Item.id == request.form['item_id']).first() is None:
            abort(400)

        # Download File
        path = os.path.join(APP.config['DATA_DIRECTORY'], TMP_FILE_NAME)
        file.save(path)
        file_hash = ''
        with open(path, 'rb') as tmp_file:
            # pylint: disable=E1101
            file_hash = hashlib.sha3_256(tmp_file.read()).hexdigest()
        os.rename(path, os.path.join(APP.config['DATA_DIRECTORY'], file_hash))

        new = File(item_id= request.form['item_id'], name= file.filename, file_hash= file_hash)

        try:
            DB.session.add(new)
            DB.session.commit()
            return new
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)


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
