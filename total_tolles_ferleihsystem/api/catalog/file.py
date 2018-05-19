"""
This module contains all API endpoints for the namespace 'file'
"""

import os
from flask import request
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError

from ..models import FILE_GET
from ...db_models.item import Item, File

from .. import API
from ... import DB

from ...file_store import save

TMP_FILE_NAME = 'tmp.upload'


PATH: str = '/catalog/files'
ANS = API.namespace('file', description='The file Endpoints', path=PATH)


@ANS.route('/')
class FileList(Resource):
    """
    Files root element
    """

    @API.marshal_list_with(FILE_GET)
    def get(self):
        """
        Get a list of files
        """
        return File.query.all()

    @API.marshal_with(FILE_GET)
    #TODO Add security and swagger doc
    def post(self):
        """
        Create a file
        """
        #FIXME Do better aborts and error checking
        if 'file' not in request.files:
            abort(400)
        file = request.files['file']
        if not file:
            abort(400)
        if file.filename == '':
            abort(400)
        item_id = request.form['item_id']
        if item_id is None:
            abort(400)
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(400)

        file_hash = save(file)
        name, ext = os.path.splitext(file.filename)
        new = File(item_id=item_id, name=name, file_type=ext, file_hash=file_hash)

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

    @ANS.response(404, 'Requested item not found!')
    @API.marshal_with(FILE_GET)
    def get(self, file_id):
        """
        Get a single file object
        """
        file = File.query.filter(File.id == file_id).first()
        if file is None:
            abort(404, 'Requested item not found!')

        return file

    @ANS.response(404, 'Requested item not found!')
    @ANS.response(204, 'Success.')
    def delete(self, file_id):
        """
        Delete a file object
        """
        file = File.query.filter(File.id == file_id).first()
        if file is None:
            abort(404, 'Requested item not found!')
        DB.session.delete(file)
        DB.session.commit()
        return "", 204

    def put(self, file_id):
        """
        Replace a file object
        """
        pass


PATH2: str = '/file-store'
ANS2 = API.namespace('file', description='The download Endpoint to download any file from the system.', path=PATH)

@ANS2.route('/<string:file_hash>/')
class FileData(Resource):
    """
    The endpoints to get the actual stored file
    """

    def get(self, file_hash):
        """
        Get the actual file
        """
        pass
