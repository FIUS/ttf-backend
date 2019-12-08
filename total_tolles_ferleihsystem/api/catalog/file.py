"""
This module contains all API endpoints for the namespace 'file'
"""

import os
from typing import Tuple
# pylint: disable=E0611
from hashlib import sha3_256
from flask import request, make_response
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from total_tolles_ferleihsystem.tasks.file import create_archive
from ..models import FILE_GET, FILE_PUT
from ...login import UserRole
from ...db_models.item import Item, File

from .. import API, satisfies_role
from ... import APP, DB



PATH: str = '/catalog/files'
ANS = API.namespace('file', description='The file Endpoints', path=PATH)

@ANS.route('/')
class FileList(Resource):
    """
    Files root element
    """

    @jwt_required
    @API.marshal_list_with(FILE_GET)
    def get(self):
        """
        Get a list of files
        """
        base_query = File.query.options(joinedload('item'))

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((File.visible_for == 'all') | (File.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(File.visible_for == 'all')

        return base_query.all()

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=FILE_GET)
    @ANS.response(201, 'File created.')
    @ANS.response(400, 'Wrongly formated request! Missing file or item.')
    @ANS.response(404, 'Requested item was not found!')
    @ANS.response(500, 'SQL Error!')
    def post(self):
        """
        Create a file
        """
        #FIXME Do better aborts and error checking and maybe logging
        if 'file' not in request.files:
            abort(400, 'No file attached!')
        file = request.files['file']
        if not file:
            abort(400, 'File Empty!')
        if file.filename is None or file.filename == '':
            abort(400, 'No file name!')
        item_id = request.form['item_id']
        if item_id is None:
            abort(400, 'No item specified!')
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item was not found!')

        # calculate the file hash and reset the file read pointer
        file_hash = sha3_256(file.stream.read()).hexdigest()
        file.stream.seek(0)

        # generate the item object
        __name, ext = os.path.splitext(file.filename)
        new = File(item_id=item_id, name='', file_type=ext, file_hash=file_hash)

        # save the file to disk
        with open(os.path.join(APP.config['DATA_DIRECTORY'], file_hash), mode='wb') as file_on_disk:
            file_on_disk.write(file.stream.read())

        # add the file to the sql database
        DB.session.add(new)
        DB.session.commit()
        return marshal(new, FILE_GET), 201


@ANS.route('/<int:file_id>/')
class FileDetail(Resource):
    """
    Single file object
    """

    @jwt_required
    @ANS.response(404, 'Requested file not found!')
    @API.marshal_with(FILE_GET)
    def get(self, file_id):
        """
        Get a single file object
        """
        base_query = File.query.filter(File.id == file_id).options(joinedload('item'))

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((File.visible_for == 'all') | (File.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(File.visible_for == 'all')

        file = base_query.first()

        if file is None:
            APP.logger.debug('Requested file not found for id: %s !', file_id)
            abort(404, 'Requested file not found!')

        return file

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(204, 'Success.')
    @ANS.response(404, 'Requested file not found!')
    def delete(self, file_id):
        """
        Delete a file object
        """
        file = File.query.filter(File.id == file_id).first()

        if file is None:
            APP.logger.debug('Requested file not found for id: %s !', file_id)
            abort(404, 'Requested file not found!')

        DB.session.delete(file)
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=FILE_PUT)
    @ANS.response(404, 'Requested file not found!')
    @ANS.response(500, 'SQL Error!')
    @ANS.marshal_with(FILE_GET)
    def put(self, file_id):
        """
        Replace a file object
        """
        file = File.query.filter(File.id == file_id).options(joinedload('item')).first()

        if file is None:
            APP.logger.debug('Requested file not found for id: %s !', file_id)
            abort(404, 'Requested file not found!')

        file.update(**request.get_json())

        DB.session.commit()
        return file


@ANS.route('/archive')
class ArchiveHandler(Resource):
    """
    Archive Endpoints
    """

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @API.param('name', 'The name of the archive file', type=str, required=False, default='archive')
    @API.param('file', 'The file_ids to be added to the archive', type=str, required=True)
    @ANS.response(202, 'Archive is currently generated.')
    @ANS.response(500, 'SQL Error!')
    def post(self):
        """
        Create a Archive of files
        """
        abort(501, 'Currently not implemented!!') # TODO fix archive endpoint

        file_name = request.args.get('name', default='archive', type=str)
        file_ids = request.args.getlist('file', type=int)

        def map_function(file_id: int) -> Tuple[str, str]:
            """
            Inline function which maps the id to its file entry
            """
            file = File.query.filter(File.id == file_id).first()
            return (file.file_hash, file.name + file.file_type)

        new = File(name=file_name, file_type='.zip', file_hash=None)

        try:
            DB.session.add(new)
            DB.session.commit()

            # Run task
            create_archive.delay(new.id, list(map(map_function, file_ids)))

            return marshal(new, FILE_GET), 202
        except IntegrityError:
            abort(500, 'SQL Error!')


PATH2: str = '/file-store'
ANS2 = API.namespace('file', description='The download Endpoint to download any file from the system.', path=PATH2)

@ANS2.route('/<int:file_id>/')
class FileData(Resource):
    """
    The endpoints to get the actual stored file
    """

    @jwt_required
    @ANS.response(404, 'Requested file not found!')
    @ANS.response(500, 'Something crashed while reading file!')
    def get(self, file_id):
        """
        Get the actual file
        """
        base_query = File.query.filter(File.id == file_id).options(joinedload('item'))

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((File.visible_for == 'all') | (File.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(File.visible_for == 'all')

        file = base_query.first()

        if file is None:
            APP.logger.debug('Requested file not found for id: %s !', file_id)
            abort(404, 'Requested file was not found!')

        headers = {
            "Content-Disposition": "attachment; filename={}".format(file.item.name + file.name + file.file_type)
        }

        with open(os.path.join(APP.config['DATA_DIRECTORY'], file.file_hash), mode='rb') as file_on_disk:
            return make_response(file_on_disk.read(), headers)

        APP.logger.error('Crash while downloading file: %s !', file_id)
        abort(500, 'Something crashed while reading file!')
