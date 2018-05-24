"""
This module contains all API endpoints for the namespace 'file'
"""

import os
from typing import Tuple
from flask import request, make_response
from flask_restplus import Resource, abort
from sqlalchemy.exc import IntegrityError

from ..models import FILE_GET, FILE_PUT
from ...db_models.item import Item, File

from .. import API
from ... import DB

from ...file_store import save_file, read_file, create_archive


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

        file_hash = save_file(file)
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

    @ANS.response(404, 'Requested file not found!')
    @API.marshal_with(FILE_GET)
    def get(self, file_id):
        """
        Get a single file object
        """
        file = File.query.filter(File.id == file_id).first()
        if file is None:
            abort(404, 'Requested item not found!')

        return file

    @ANS.response(404, 'Requested file not found!')
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

    @ANS.doc(model=FILE_GET, body=FILE_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Requested file not found!')
    @ANS.marshal_with(FILE_GET)
    def put(self, file_id):
        """
        Replace a file object
        """
        file = File.query.filter(File.id == file_id).first()
        if file is None:
            abort(404, 'Requested file not found!')

        file.update(**request.get_json())

        try:
            DB.session.commit()
            return file
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)


@ANS.route('/archive')
class ArchiveHandler(Resource):
    """
    Archive Endpoints
    """

    @API.param('name', 'The name of the archive file', type=str, required=False, default='archive')
    @API.param('file', 'The file_ids to be added to the archive', type=str, required=True)
    def post(self):
        """
        Create a Archive of files
        """
        file_name = request.args.get('name', default='archive', type=str)
        file_ids = request.args.getlist('file', type=int)

        def map_function(file_id: int) -> Tuple[str, str]:
            """
            Inline function which maps the id to its file entry
            """
            file = File.query.filter(File.id == file_id).first()
            return (file.file_hash, file.name + file.file_type)

        archive_hash = create_archive(file_ids.map(map_function))
        new = File(name=file_name, file_type='.zip', file_hash=archive_hash)

        try:
            DB.session.add(new)
            DB.session.commit()
            return new
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)


PATH2: str = '/file-store'
ANS2 = API.namespace('file', description='The download Endpoint to download any file from the system.', path=PATH2)

@ANS2.route('/<string:file_hash>/')
class FileData(Resource):
    """
    The endpoints to get the actual stored file
    """

    def get(self, file_hash):
        """
        Get the actual file
        """
        file = File.query.filter(File.file_hash == file_hash).first()

        headers = {
            "Content-Disposition": "attachment; filename={}".format(file.name + file.file_type)
        }
        return make_response((read_file(file_hash), headers))
