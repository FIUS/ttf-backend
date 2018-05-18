"""
This module contains all API endpoints for the namespace 'item_type'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ..models import ITEM_TYPE_GET, ITEM_TYPE_POST, ATTRIBUTE_DEFINITION_GET, ID, ITEM_TYPE_PUT
from ... import DB
from ...login import UserRole

from ...db_models.attributeDefinition import AttributeDefinition
from ...db_models.itemType import ItemType, ItemTypeToAttributeDefinition, ItemTypeToItemType
from ...db_models.item import Item 

PATH: str = '/catalog/item_types'
ANS = API.namespace('item_type', description='ItemTypes', path=PATH)


@ANS.route('/')
class ItemTypeList(Resource):
    """
    Item types root element
    """

    @jwt_required
    @API.param('deleted', 'get all deleted objects (and only these)', type=bool, required=False, default=False)
    @API.marshal_list_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item types currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return ItemType.query.filter(ItemType.deleted == test_for).order_by(ItemType.name).all()

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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
            DB.session.add(new)
            DB.session.commit()
            return marshal(new, ITEM_TYPE_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:type_id>/')
class ItemTypeDetail(Resource):
    """
    Single item type object
    """

    @jwt_required
    @ANS.response(404, 'Requested item type not found!')
    @API.marshal_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get a single item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type not found!')
        return item_type

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, type_id):
        """
        Delete a item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type not found!')
        item_type.deleted = True
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, type_id):
        """
        Undelete a item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type not found!')
        item_type.deleted = False
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=ITEM_TYPE_GET, body=ITEM_TYPE_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Requested item type not found!')
    # pylint: disable=R0201
    def put(self, type_id):
        """
        Replace a item type object
        """
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(404, 'Requested item type not found!')
        item_type.update(**request.get_json())
        try:
            DB.session.commit()
            return marshal(item_type, ITEM_TYPE_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)


@ANS.route('/<int:type_id>/attributes/')
class ItemTypeAttributes(Resource):
    """
    The attributes of a single item type object
    """

    @jwt_required
    @ANS.response(404, 'Requested item type not found!')
    @API.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get all attribute definitions for this item type.
        """
        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')

        associations = (ItemTypeToAttributeDefinition
                        .query
                        .filter(ItemTypeToAttributeDefinition.item_type_id == type_id)
                        .all())
        return [element.attribute_definition for element in associations]

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=ATTRIBUTE_DEFINITION_GET, body=ID)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(400, 'Requested attribute definition not found!')
    @ANS.response(409, 'Attribute definition is already associated with this item type!')
    @API.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def post(self, type_id):
        """
        Associate a new attribute definition with the item type.
        """
        attribute_definition_id = request.get_json()["id"]
        attribute_definition = AttributeDefinition.query.filter(AttributeDefinition.id == attribute_definition_id).first()


        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')
        if attribute_definition is None:
            abort(400, 'Requested attribute definition not found!')

        items = Item.query.filter(Item.type_id == type_id).all()

        new = ItemTypeToAttributeDefinition(type_id, attribute_definition_id)
        try:
            DB.session.add(new)
            for item in items:
                DB.session.add_all(item.get_new_attributes([attribute_definition]))
            DB.session.commit()
            associations = (ItemTypeToAttributeDefinition
                            .query
                            .filter(ItemTypeToAttributeDefinition.item_type_id == type_id)
                            .all())
            return [e.attribute_definition for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Attribute definition is already asociated with item type!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ID)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(400, 'Requested attribute definition not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, type_id):
        """
        Remove association of a attribute definition with the item type.
        """
        attribute_definition_id = request.get_json()["id"]

        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')
        if AttributeDefinition.query.filter(AttributeDefinition.id == attribute_definition_id).first() is None:
            abort(400, 'Requested attribute definition not found!')

        association = (ItemTypeToAttributeDefinition
                       .query
                       .filter(ItemTypeToAttributeDefinition.item_type_id == type_id)
                       .filter(ItemTypeToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                       .first())
        if association is None:
            return '', 204
        try:
            DB.session.delete(association)
            DB.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)


@ANS.route('/<int:type_id>/can_contain/')
class ItemTypeCanContainTypes(Resource):
    """
    The item types that a item of this type can contain.
    """

    @jwt_required
    @ANS.response(404, 'Requested item type not found!')
    @API.marshal_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def get(self, type_id):
        """
        Get all item types, this item_type may contain.
        """
        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')

        associations = ItemTypeToItemType.query.filter(ItemTypeToItemType.parent_id == type_id).all()
        return [e.item_type for e in associations]

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=ITEM_TYPE_GET, body=ID)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(400, 'Requested child item type not found!')
    @ANS.response(409, 'Item type can already be contained in this item type.')
    @API.marshal_with(ITEM_TYPE_GET)
    # pylint: disable=R0201
    def post(self, type_id):
        """
        Add new item type to be able to be contained in this item type.
        """
        child_id = request.get_json()["id"]


        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')
        if ItemType.query.filter(ItemType.id == child_id).first() is None:
            abort(400, 'Requested attribute definition not found!')

        new = ItemTypeToItemType(type_id, child_id)
        try:
            DB.session.add(new)
            DB.session.commit()
            associations = ItemTypeToItemType.query.filter(ItemTypeToItemType.parent_id == type_id).all()
            return [e.item_type for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Item type can already be contained in this item type.')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ID)
    @ANS.response(404, 'Requested item type not found!')
    @ANS.response(400, 'Requested child item type not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, type_id):
        """
        Remove item type from being able to be contained in this item type
        """
        child_id = request.get_json()["id"]


        if ItemType.query.filter(ItemType.id == type_id).first() is None:
            abort(404, 'Requested item type not found!')
        if ItemType.query.filter(ItemType.id == child_id).first() is None:
            abort(400, 'Requested attribute definition not found!')

        association = (ItemTypeToItemType
                       .query
                       .filter(ItemTypeToItemType.parent_id == type_id)
                       .filter(ItemTypeToItemType.item_type_id == child_id)
                       .first())
        if association is None:
            return '', 204
        try:
            DB.session.delete(association)
            DB.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)
