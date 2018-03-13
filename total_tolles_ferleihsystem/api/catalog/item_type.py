"""
This module contains all API endpoints for the namespace 'item_type'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import item_type_get, item_type_post
from ... import db

from ...db_models.itemType import ItemType

PATH: str = '/catalog/item_types'
ANS = api.namespace('item_type', description='ItemTypes', path=PATH)


@ANS.route('/')
class ItemTypeList(Resource):
    """
    Item types root element
    """

    @api.doc(security=None)
    @api.marshal_list_with(item_type_get)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item types currently in the system
        """
        return ItemType.query.all()

    @api.doc(security=None)
    @ANS.doc(model=item_type_get, body=item_type_post)
    @ANS.response(409, 'Name is not Unique.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item type to the system
        """
        new = ItemType(**request.get_json())
        try:
            db.session.add(new)
            db.session.commit()
            return marshal(new, item_type_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:id>/')
class ItemTypeDetail(Resource):
    """
    Single item type element
    """

    @api.doc(security=None)
    @api.marshal_with(item_type_get)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get a single item type object
        """
        return ItemType.query.filter(ItemType.id == type_id).first()

    @ANS.response(404, 'Item type not found.')
    # pylint: disable=R0201
    def delete(self, type_id):
        """
        Delete a item type object
        """
        item_type = ItemType.get_by_id(type_id)
        if item_type is None:
            abort(404, 'Requested item type was not found!')
        db.session.delete(item_type)
        db.session.commit()
