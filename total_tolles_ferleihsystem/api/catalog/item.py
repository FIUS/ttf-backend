"""
This module contains all API endpoints for the namespace 'item'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ITEM_GET, ITEM_POST, ID, ITEM_PUT, ITEM_TAG_GET, ATTRIBUTE
from ... import db

from ...db_models.item import Item, ItemToTag, Attributes

PATH: str = '/catalog/item'
ANS = api.namespace('item', description='Items', path=PATH)


@ANS.route('/')
class ItemList(Resource):
    """
    Items root element
    """

    @api.doc(security=None)
    @api.param('deleted', 'get all deleted elements (and only these)', type=bool, required=False, default=False)
    @api.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all items currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return Item.query.filter(Item.deleted == test_for).all()

    @api.doc(security=None)
    @ANS.doc(model=ITEM_GET, body=ITEM_POST)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item to the system
        """
        new = Item(**request.get_json())
        try:
            db.session.add(new)
            db.session.commit()
            return marshal(new, ITEM_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:item_id>/')
class ItemDetail(Resource):
    """
    Single item element
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get a single item object
        """
        item = Item.query.filter(Item.id == item_id).first()

        return item
    @ANS.response(404, 'Item not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Delete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item was not found!')
        item.deleted = True
        db.session.commit()
        return "", 204
    @ANS.response(404, 'Item not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Undelete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item was not found!')
        item.deleted = False
        db.session.commit()
        return "", 204
    @ANS.doc(model=ITEM_GET, body=ITEM_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Item not found.')
    def put(self, item_id):
        """
        Replace a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item was not found!')
        item.update(**request.get_json())
        try:
            db.session.commit()
            return marshal(item, ITEM_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:item_id>/tags')
class ItemItemTags(Resource):
    """
    The item tags of a single item
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all tags for this item.
        """

        associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
        return [e.tag for e in associations]

    @api.doc(security=None)
    @api.marshal_with(ITEM_TAG_GET)
    @ANS.doc(model=ITEM_TAG_GET, body=ID)
    @ANS.response(409, 'Tag is already associated with this item!')
    # pylint: disable=R0201
    def post(self,item_id):
        """
        Associate a new tag with the item.
        """
        new = ItemToTag(item_id,request.get_json()["id"])
        try:
            db.session.add(new)
            db.session.commit()
            associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
            return [e.tag for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Tag is already associated with this item!')
            abort(500)

    @api.doc(security=None)
    @ANS.doc(body=ID)
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self,item_id):
        """
        Remove association of a tag with the item.
        """
        association = (ItemToTag.query
                                .filter(ItemToTag.tag_id == item_id)
                                .filter(ItemToTag.attribute_definition_id == request.get_json()["id"])
                                .first())
        if association is None: 
            return '', 204
        try:
            db.session.delete(association)
            db.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)

@ANS.route('/<int:item_id>/attributes')
class ItemAttributes(Resource):
    """
    The attributes of a single item
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all attributes for this item.
        """

        return Attributes.query.filter(Attributes.item_id == item_id).all()
