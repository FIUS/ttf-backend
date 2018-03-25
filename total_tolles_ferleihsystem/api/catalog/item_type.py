"""
This module contains all API endpoints for the namespace 'item_type'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ITEM_TYPE_GET, ITEM_TYPE_POST, ATTRIBUTE_DEFINITION_GET, ID, ITEM_TYPE_PUT
from ... import db

from ...db_models.itemType import ItemType, ItemTypeToAttributeDefinition, ItemTypeToItemType

PATH: str = '/catalog/item_types'
ANS = api.namespace('item_type', description='ItemTypes', path=PATH)


@ANS.route('/')
class ItemTypeList(Resource):
    """
    Item types root element
    """

    @api.doc(security=None)
    @api.param('deleted', 'get all deleted elements (and only these)', type=bool, required=False, default=False)
    @api.marshal_list_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item types currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return ItemType.query.filter(ItemType.deleted == test_for).all()

    @api.doc(security=None)
    @ANS.doc(model=ITEM_TYPE_GET, body=ITEM_TYPE_POST)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item type to the system
        """
        new = ItemType(**request.get_json())
        try:
            db.session.add(new)
            db.session.commit()
            return marshal(new, ITEM_TYPE_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:type_id>/')
class ItemTypeDetail(Resource):
    """
    Single item type element
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get a single item type object
        """
        return ItemType.query.filter(ItemType.id == type_id).first()

    @ANS.response(404, 'Item type not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, type_id):
        """
        Delete a item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type was not found!')
        item_type.deleted = True
        db.session.commit()
        return "", 204
    @ANS.response(404, 'Item type not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, type_id):
        """
        Undelete a item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type was not found!')
        item_type.deleted = False
        db.session.commit()
        return "", 204
    @ANS.doc(model=ITEM_TYPE_GET, body=ITEM_TYPE_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Item type not found.')
    def put(self, type_id):
        """
        Replace a item tag object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item tag was not found!')
        item_type.update(**request.get_json())
        try:
            db.session.commit()
            return marshal(item_type, ITEM_TYPE_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)


@ANS.route('/<int:type_id>/attributes/')
class ItemTypeAttributes(Resource):
    """
    The attributes of a single item type element
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get all attribute definitions for this item type.
        """
        associations = ItemTypeToAttributeDefinition.query.filter(ItemTypeToAttributeDefinition.item_type_id == type_id).all()
        return [e.attribute_definition for e in associations]

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_DEFINITION_GET)
    @ANS.doc(model=ATTRIBUTE_DEFINITION_GET, body=ID)
    @ANS.response(409, 'Attribute definition is already associated with this item type!')
    # pylint: disable=R0201
    def post(self,type_id):
        """
        Associate a new attribute definition with the item type.
        """
        new = ItemTypeToAttributeDefinition(type_id,request.get_json()["id"])
        try:
            db.session.add(new)
            db.session.commit()
            associations = ItemTypeToAttributeDefinition.query.filter(ItemTypeToAttributeDefinition.item_type_id == type_id).all()
            return [e.attribute_definition for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Attribute definition is already asociated with item type!')
            abort(500)

    @api.doc(security=None)
    @ANS.doc(body=ID)
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self,type_id):
        """
        Remove association of a attribute definition with the item type.
        """
        association = (ItemTypeToAttributeDefinition.query
                                                    .filter(ItemTypeToAttributeDefinition.item_type_id == type_id)
                                                    .filter(ItemTypeToAttributeDefinition.attribute_definition_id == request.get_json()["id"])
                                                    .first())
        if association is None:
            return '', 204
        try:
            db.session.delete(association)
            db.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)


@ANS.route('/<int:type_id>/can_contain/')
class ItemTypeCanContainTypes(Resource):
    """
    The item types that a item of this type can contain.
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get all item types, this item_type may contain.
        """
        associations = ItemTypeToItemType.query.filter(ItemTypeToItemType.parent_id == type_id).all()
        return [e.item_type for e in associations]

    @api.doc(security=None)
    @api.marshal_with(ITEM_TYPE_GET)
    @ANS.doc(model=ITEM_TYPE_GET, body=ID)
    @ANS.response(409, 'Item type can already be contained in this item type.')
    # pylint: disable=R0201
    def post(self,type_id):
        """
        Add new item type to be able to be contained in this item type.
        """
        new = ItemTypeToItemType(type_id,request.get_json()["id"])
        try:
            db.session.add(new)
            db.session.commit()
            associations = ItemTypeToItemType.query.filter(ItemTypeToItemType.parent_id == type_id).all()
            return [e.item_type for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Item type can already be contained in this item type.')
            abort(500)

    @api.doc(security=None)
    @ANS.doc(body=ID)
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self,type_id):
        """
        Remove item type from being able to be contained in this item type
        """
        association = (ItemTypeToItemType.query
                                         .filter(ItemTypeToItemType.parent_id == type_id)
                                         .filter(ItemTypeToItemType.item_type_id == request.get_json()["id"])
                                         .first())
        if association is None:
            return '', 204
        try:
            db.session.delete(association)
            db.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)
