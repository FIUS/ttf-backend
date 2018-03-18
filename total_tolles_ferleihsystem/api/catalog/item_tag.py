"""
This module contains all API endpoints for the namespace 'item_tag'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ITEM_TAG_GET, ITEM_TAG_POST
from ... import db

from ...db_models.tag import Tag

PATH: str = '/catalog/item_tags'
ANS = api.namespace('item_tag', description='ItemTags', path=PATH)


@ANS.route('/')
class ItemTags(Resource):
    """
    Item tags root element
    """

    @api.doc(security=None)
    @api.marshal_list_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item tags currently in the system
        """
        return Tag.query.filter(Tag.deleted == False).all()

    @api.doc(security=None)
    @ANS.doc(model=ITEM_TAG_GET, body=ITEM_TAG_POST)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item tag to the system
        """
        new = Tag(**request.get_json())
        try:
            db.session.add(new)
            db.session.commit()
            return marshal(new, ITEM_TAG_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:tag_id>/')
class ItemTagDetail(Resource):
    """
    Single item tag element
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self, tag_id):
        """
        Get a single item tag object
        """
        return Tag.query.filter(Tag.id == tag_id).first()

    @ANS.response(404, 'Item tag not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, tag_id):
        """
        Delete a item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        if item_tag is None:
            abort(404, 'Requested item tag was not found!')
        item_tag.deleted = True
        db.session.commit()
        return "", 204
