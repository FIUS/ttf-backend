"""
This module contains all API endpoints for the namespace 'item'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ITEM_GET, ITEM_POST, ID, ITEM_PUT, ITEM_TAG_GET, ATTRIBUTE_PUT, ATTRIBUTE_GET, ATTRIBUTE_GET_FULL
from ... import db

from ...db_models.item import Item, ItemToTag, ItemAttribute
from ...db_models.itemType import ItemTypeToAttributeDefinition, ItemType
from ...db_models.tag import TagToAttributeDefinition, Tag

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
    @ANS.response(400, 'Requested item type not found!')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new item to the system
        """
        item_type = ItemType.query.filter(ItemType.id == request.get_json()["type_id"]).first()
        if item_type is None:
            abort(400, 'Requested item type not found!')

        new = Item(**request.get_json())

        try:
            db.session.add(new)
            item_id = new.id
            type_id = new.type_id
            item_type_attribute_definitions = (ItemTypeToAttributeDefinition
                                               .query
                                               .filter(ItemTypeToAttributeDefinition.item_type_id == type_id)
                                               .all())
            attributes = []
            for element in item_type_attribute_definitions:
                attributes.append(ItemAttribute(item_id,
                                                element.attribute_definition_id,
                                                "")) #TODO: Get default if possible.
            db.session.add_all(attributes)
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
    Single item object
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_GET)
    @ANS.response(404, 'Requested item not found!')
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get a single item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')

        return item

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
        db.session.commit()
        return "", 204

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
        db.session.commit()
        return "", 204

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
        
        item_type = ItemType.query.filter(ItemType.id == request.get_json()["type_id"]).first()
        if item_type is None:
            abort(400, 'Requested item type not found!')

        item.update(**request.get_json())
        try:
            db.session.commit()
            return marshal(item, ITEM_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:item_id>/tags/')
class ItemItemTags(Resource):
    """
    The item tags of a single item
    """

    @api.doc(security=None)
    @api.marshal_with(ITEM_TAG_GET)
    @ANS.response(404, 'Requested item not found!')
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all tags for this item.
        """
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
        return [e.tag for e in associations]

    @api.doc(security=None)
    @api.marshal_with(ITEM_TAG_GET)
    @ANS.doc(model=ITEM_TAG_GET, body=ID)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item tag not found!')
    @ANS.response(409, 'Tag is already associated with this item!')
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Associate a new tag with the item.
        """
        tag_id = request.get_json()["id"]

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')
        if Tag.query.filter(Tag.id == tag_id).first() is None:
            abort(400, 'Requested item tag not found!')

        new = ItemToTag(item_id, tag_id)
        attributes = ItemAttribute.query.filter(ItemAttribute.item_id == item_id).all()

        attributes_dict = {}
        new_attributes = []

        for element in attributes:
            attributes_dict[element.attribute_definition_id] = element.value

        item_tag_attribute_definitions = (TagToAttributeDefinition
                                          .query
                                          .filter(TagToAttributeDefinition.tag_id == tag_id)
                                          .all())
        for element in item_tag_attribute_definitions:
            if not element.attribute_definition_id in attributes_dict:
                attributes_dict[element.attribute_definition_id] = ""
                new_attributes.append(ItemAttribute(item_id,
                                                    element.attribute_definition_id,
                                                    "")) #TODO: Get default values
        try:
            db.session.add(new)
            db.session.add_all(new_attributes)
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
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item tag not found!')
    @ANS.response(400, 'Cannot unassociate that tag without loosing attributes.')
    @ANS.response(204, 'Success.')
    @api.param('force', 'Force removing the association. Delete attributes of this item if necessary.', type=bool, required=False, default=False)
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Remove association of a tag with the item.
        """
        tag_id = request.get_json()["id"]
        item = Item.query.filter(Item.id == item_id).first()
        tag = Tag.query.filter(Tag.id == tag_id).first()
        force = request.args.get('force', 'false') == 'true'
        if item is None:
            abort(404, 'Requested item not found!')
        if tag is None:
            abort(400, 'Requested item tag not found!')

        if not (force or item.can_tag_be_unassociated_safely(tag)):
            abort(400, 'Cannot unassociate that tag without loosing attributes.')

        association = (ItemToTag
                       .query
                       .filter(ItemToTag.item_id == item_id)
                       .filter(ItemToTag.tag_id == tag_id)
                       .first())

        if association is None:
            return '', 204
        
        try:
            db.session.delete(association)
            if force:
                for element in item.get_attributes_that_need_deletion_when_unassociating_tag(tag):
                    db.session.delete(element)
            db.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)

@ANS.route('/<int:item_id>/attributes/')
class ItemAttributeList(Resource):
    """
    The attributes of a single item
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_GET)
    @ANS.response(404, 'Requested item not found!')
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get the attributes of this item.
        """
        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        return ItemAttribute.query.filter(ItemAttribute.item_id == item_id).all()

@ANS.route('/<int:item_id>/attributes/<int:attribute_definition_id>/')
class ItemAttributeDetail(Resource):
    """
    A single attribute of this item
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_GET_FULL)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, "This item doesn't have that type of attribute!")
    # pylint: disable=R0201
    def get(self, item_id, attribute_definition_id):
        """
        Get a single attribute of this item.
        """

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        attribute = (ItemAttribute
                     .query
                     .filter(ItemAttribute.item_id == item_id)
                     .filter(ItemAttribute.attribute_definition_id == attribute_definition_id)
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        return attribute

    @api.marshal_with(ATTRIBUTE_GET_FULL)
    @ANS.doc(model=ATTRIBUTE_PUT, body=ATTRIBUTE_GET_FULL)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, "This item doesn't have that type of attribute!")
    # pylint: disable=R0201
    def put(self, item_id, attribute_definition_id):
        """
        Set a single attribute of this item.
        """

        if Item.query.filter(Item.id == item_id).first() is None:
            abort(404, 'Requested item not found!')

        value = request.get_json()["value"]
        attribute = (ItemAttribute
                     .query
                     .filter(ItemAttribute.item_id == item_id)
                     .filter(ItemAttribute.attribute_definition_id == attribute_definition_id)
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        attribute.value = value
        try:
            db.session.commit()
            return attribute
        except IntegrityError:
            abort(500)
