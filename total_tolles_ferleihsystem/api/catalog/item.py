"""
This module contains all API endpoints for the namespace 'item'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ..models import ITEM_GET, ITEM_POST, ID, ITEM_PUT, ITEM_TAG_GET, ATTRIBUTE_PUT, ATTRIBUTE_GET
from ... import DB
from ...login import UserRole

from ...db_models.item import Item, ItemToTag, ItemToAttributeDefinition, ItemToItem
from ...db_models.itemType import ItemTypeToAttributeDefinition, ItemType, ItemTypeToItemType
from ...db_models.tag import TagToAttributeDefinition, Tag
from ...db_models.attributeDefinition import AttributeDefinition

PATH: str = '/catalog/items'
ANS = API.namespace('item', description='Items', path=PATH)


@ANS.route('/')
class ItemList(Resource):
    """
    Items root element
    """

    @jwt_required
    @API.param('deleted', 'get all deleted elements (and only these)', type=bool, required=False, default=False)
    @API.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all items currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return Item.query.filter(Item.deleted == test_for).order_by(Item.name).all()

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=ITEM_GET, body=ITEM_POST)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(400, 'Requested item type not found!')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item to the system
        """
        type_id = request.get_json()["type_id"]
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(400, 'Requested item type not found!')

        new = Item(**request.get_json())

        try:
            DB.session.add(new)
            DB.session.commit()
            DB.session.add_all(new.get_new_attributes_from_type(type_id))
            DB.session.commit()
            return marshal(new, ITEM_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:item_id>/')
class ItemDetail(Resource):
    """
    Single item object
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get a single item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')

        return item

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Delete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')
        item.deleted = True
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Undelete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')
        item.deleted = False
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=ITEM_GET, body=ITEM_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item type not found!')
    # pylint: disable=R0201
    def put(self, item_id):
        """
        Replace a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')

        type_id = request.get_json()["type_id"]
        item_type = ItemType.query.filter(ItemType.id == type_id).first()
        if item_type is None:
            abort(400, 'Requested item type not found!')
        try:
            item.update(**request.get_json())
            DB.session.add_all(item.get_new_attributes_from_type(type_id))
            DB.session.commit()
            return marshal(item, ITEM_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!:' + message)
            abort(500)

@ANS.route('/<int:item_id>/tags/')
class ItemItemTags(Resource):
    """
    The item tags of a single item
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all tags for this item.
        """
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
        return [e.tag for e in associations]

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=ITEM_TAG_GET, body=ID)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item tag not found!')
    @ANS.response(409, 'Tag is already associated with this item!')
    @API.marshal_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Associate a new tag with the item.
        """
        tag_id = request.get_json()["id"]
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')
        tag = Tag.query.filter(Tag.id == tag_id).first()
        if tag is None:
            abort(400, 'Requested item tag not found!')

        new = ItemToTag(item_id, tag_id)
       
        try:
            DB.session.add(new)
            DB.session.add_all(item.get_new_attributes_from_tag(tag_id))
            DB.session.commit()
            associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
            return [e.tag for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Tag is already associated with this item!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(body=ID)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item tag not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Remove association of a tag with the item.
        """
        tag_id = request.get_json()["id"]

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')
        if Tag.query.filter(Tag.id == tag_id).first() is None:
            abort(400, 'Requested item tag not found!')

        association = (ItemToTag
                       .query
                       .filter(ItemToTag.item_id == item_id)
                       .filter(ItemToTag.tag_id == tag_id)
                       .first())

        if association is None:
            return '', 204

        try:
            DB.session.delete(association)
            DB.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)

@ANS.route('/<int:item_id>/attributes/')
class ItemAttributeList(Resource):
    """
    The attributes of a single item
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_with(ATTRIBUTE_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get the attributes of this item.
        """
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        return ItemToAttributeDefinition.query.filter(ItemToAttributeDefinition.item_id == item_id).join(ItemToAttributeDefinition.attribute_definition).order_by(AttributeDefinition.name).all()

@ANS.route('/<int:item_id>/attributes/<int:attribute_definition_id>/')
class ItemAttributeDetail(Resource):
    """
    A single attribute of this item
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, "This item doesn't have that type of attribute!")
    @API.marshal_with(ATTRIBUTE_GET)
    # pylint: disable=R0201
    def get(self, item_id, attribute_definition_id):
        """
        Get a single attribute of this item.
        """

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        attribute = (ItemToAttributeDefinition
                     .query
                     .filter(ItemToAttributeDefinition.item_id == item_id)
                     .filter(ItemToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        return attribute

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=ATTRIBUTE_PUT, body=ATTRIBUTE_GET)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, "This item doesn't have that type of attribute!")
    @API.marshal_with(ATTRIBUTE_GET)
    # pylint: disable=R0201
    def put(self, item_id, attribute_definition_id):
        """
        Set a single attribute of this item.
        """

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        value = request.get_json()["value"]
        attribute = (ItemToAttributeDefinition
                     .query
                     .filter(ItemToAttributeDefinition.item_id == item_id)
                     .filter(ItemToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        attribute.value = value
        try:
            DB.session.commit()
            return attribute
        except IntegrityError:
            abort(500)

@ANS.route('/<int:item_id>/contained/')
class ItemContainedItems(Resource):
    """
    The items contained in this item object
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all contained items of this item.
        """
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToItem.query.filter(ItemToItem.parent_id == item_id).all()
        return [e.item for e in associations]

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=ITEM_GET, body=ID)
    @ANS.response(404, 'Requested item (current) not found!')
    @ANS.response(400, 'Requested item (to be contained) not found!')
    @ANS.response(400, 'This item can not contain that item.')
    @ANS.response(409, 'Subitem is already a subitem of this item!')
    @API.marshal_with(ITEM_GET)
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Add a new contained item to this item
        """
        contained_item_id = request.get_json()["id"]
        parent = Item.query.filter(Item.id == item_id).first()
        child = Item.query.filter(Item.id == contained_item_id).first()

        if parent is None:
            abort(404, 'Requested item (current) not found!')
        if child is None:
            abort(400, 'Requested item (to be contained) not found!')

        association = (ItemTypeToItemType
                       .query
                       .filter(ItemTypeToItemType.parent_id == parent.type_id)
                       .filter(ItemTypeToItemType.item_type_id == child.type_id)
                       .first())

        if association is None:
            abort(400, 'This item can not contain that item.')

        new = ItemToItem(item_id, contained_item_id)
        try:
            DB.session.add(new)
            DB.session.commit()
            associations = ItemToItem.query.filter(ItemToItem.parent_id == item_id).all()
            return [e.item for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Attribute definition is already asociated with this tag!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(body=ID)
    @ANS.response(404, 'Requested item (current) not found!')
    @ANS.response(400, 'Requested item (to be contained) not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Remove a contained item from this item.
        """
        contained_item_id = request.get_json()["id"]

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item (current) not found!')
        if Item.query.filter(Item.id == contained_item_id).first() is None:
            abort(400, 'Requested item (to be contained) not found!')

        association = (ItemToItem
                       .query
                       .filter(ItemToItem.parent_id == item_id)
                       .filter(ItemToItem.item_id == contained_item_id)
                       .first())
        if association is None:
            return '', 204
        try:
            DB.session.delete(association)
            DB.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)
