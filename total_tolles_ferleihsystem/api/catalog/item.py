"""
This module contains all API endpoints for the namespace 'item'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ..models import ITEM_GET, ITEM_POST, ID, ITEM_PUT, ITEM_TAG_GET, ATTRIBUTE_GET, FILE_GET, LENDING_GET
from ... import DB, APP
from ...login import UserRole
from ...performance import record_view_performance

from ...db_models.item import Item, ItemToTag, ItemToAttributeDefinition, ItemToItem, File, Lending
from ...db_models.itemType import ItemType, ItemTypeToItemType
from ...db_models.tag import Tag
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
    @API.param('lent', 'get all currently lent items', type=bool, required=False, default=False)
    @API.marshal_list_with(ITEM_GET)
    @record_view_performance()
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all items currently in the system
        """
        base_query = Item.query.options(joinedload('lending'), joinedload("_tags"))
        test_for = request.args.get('deleted', 'false') == 'true'
        if test_for:
            base_query = base_query.filter(Item.deleted_time != None)
        else:
            base_query = base_query.filter(Item.deleted_time == None)

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        if request.args.get('lent', 'false') == 'true':
            base_query = base_query.filter(Item.lending_id != None)

        return base_query.order_by(Item.name).all()

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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
            attributes_to_add = new.get_new_attributes_from_type(type_id)
            DB.session.add_all(attributes_to_add)
            DB.session.commit()
            return marshal(new, ITEM_GET), 201
        except IntegrityError as err:
            message = str(err)
            print(message)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('Name is not unique. %s', err)
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
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        item = base_query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')

        return item

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'Requested item is currently lent!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, item_id):
        """
        Delete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')

        code, msg, commit = item.delete()

        if commit:
            DB.session.commit()
        if code == 204:
            return "", 204

        abort(code, msg)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, 'The type of this item does not currently exist!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, item_id):
        """
        Undelete a item object
        """
        item = Item.query.filter(Item.id == item_id).first()
        if item is None:
            abort(404, 'Requested item not found!')
        if item.type is None or item.type.deleted:
            abort(400, 'The type of this item does not currently exist!')
        item.deleted = False
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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

        attributes_to_add, attributes_to_delete, attributes_to_undelete = item.get_attribute_changes_from_type_change(item.type_id, type_id)

        try:
            item.update(**request.get_json())
            DB.session.add_all(attributes_to_add)
            for attr in attributes_to_undelete:
                attr.deleted = False
            for attr in attributes_to_delete:
                attr.deleted = True
            DB.session.commit()
            return marshal(item, ITEM_GET), 200
        except IntegrityError as err:
            message = str(err)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('Name is not unique. %s', err)
                abort(409, 'Name is not unique!')
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
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
        return [e.tag for e in associations if not e.tag.deleted]

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ID)
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
        # pylint: disable=C0121
        item = Item.query.filter(Item.id == item_id).filter(Item.deleted_time == None).first()
        if item is None:
            abort(404, 'Requested item not found!')
        # pylint: disable=C0121
        tag = Tag.query.filter(Tag.id == tag_id).filter(Tag.deleted_time == None).first()
        if tag is None:
            abort(400, 'Requested item tag not found!')

        new = ItemToTag(item_id, tag_id)

        attributes_to_add, _, attributes_to_undelete = item.get_attribute_changes_from_tag(tag_id)
        try:
            DB.session.add(new)
            DB.session.add_all(attributes_to_add)
            for attr in attributes_to_undelete:
                attr.deleted = False
            DB.session.commit()
            associations = ItemToTag.query.filter(ItemToTag.item_id == item_id).all()
            return [e.tag for e in associations]
        except IntegrityError as err:
            message = str(err)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('Tag is already associated with this item. %s', err)
                abort(409, 'Tag is already associated with this item!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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

        # pylint: disable=C0121
        item = Item.query.filter(Item.id == item_id).filter(Item.deleted_time == None).first()
        if item is None:
            abort(404, 'Requested item not found!')
        # pylint: disable=C0121
        if Tag.query.filter(Tag.id == tag_id).filter(Tag.deleted_time == None).first() is None:
            abort(400, 'Requested item tag not found!')

        association = (ItemToTag
                       .query
                       .filter(ItemToTag.item_id == item_id)
                       .filter(ItemToTag.tag_id == tag_id)
                       .first())

        if association is None:
            return '', 204

        _, attributes_to_delete, _ = item.get_attribute_changes_from_tag(tag_id, True)

        try:
            DB.session.delete(association)
            for attr in attributes_to_delete:
                attr.deleted = True
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
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        # pylint: disable=C0121
        attributes = (ItemToAttributeDefinition.query
                      .filter(ItemToAttributeDefinition.item_id == item_id)
                      .filter(ItemToAttributeDefinition.deleted_time == None)
                      .join(ItemToAttributeDefinition.attribute_definition)
                      .order_by(AttributeDefinition.name)
                      .options(joinedload('attribute_definition'))
                      .all())
        return attributes; # DON'T CHANGE THIS!!
        # It is necessary because a Flask Bug prehibits log messages on return statements.

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
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        # pylint: disable=C0121
        attribute = (ItemToAttributeDefinition
                     .query
                     .filter(ItemToAttributeDefinition.item_id == item_id)
                     .filter(ItemToAttributeDefinition.deleted_time == None)
                     .filter(ItemToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                     .options(joinedload('attribute_definition'))
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        return attribute

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ATTRIBUTE_GET)
    @ANS.response(404, 'Requested item not found!')
    @ANS.response(400, "This item doesn't have that type of attribute!")
    @API.marshal_with(ATTRIBUTE_GET)
    # pylint: disable=R0201
    def put(self, item_id, attribute_definition_id):
        """
        Set a single attribute of this item.
        """

        # pylint: disable=C0121
        if Item.query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        value = request.get_json()["value"]
        # pylint: disable=C0121
        attribute = (ItemToAttributeDefinition
                     .query
                     .filter(ItemToAttributeDefinition.item_id == item_id)
                     .filter(ItemToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                     .filter(ItemToAttributeDefinition.deleted_time == None)
                     .options(joinedload('attribute_definition'))
                     .first())

        if attribute is None:
            abort(400, "This item doesn't have that type of attribute!")

        attribute.update(value)

        try:
            DB.session.commit()
            return attribute
        except IntegrityError:
            abort(500)


@ANS.route('/<int:item_id>/parent/')
class ItemParentItems(Resource):
    """
    The parent items of this item object
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all contained items of this item.
        """
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToItem.query.filter(ItemToItem.item_id == item_id).options(joinedload('parent')).all()
        return [e.parent for e in associations if not e.item.deleted]


@ANS.route('/<int:item_id>/contained/')
class ItemContainedItems(Resource):
    """
    The items contained in this item object
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all contained items of this item.
        """
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        associations = ItemToItem.query.filter(ItemToItem.parent_id == item_id).options(joinedload('item')).all()
        return [e.item for e in associations if not e.item.deleted]

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ID)
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
        # pylint: disable=C0121
        parent = Item.query.filter(Item.id == item_id).filter(Item.deleted_time == None).first()
        # pylint: disable=C0121
        child = Item.query.filter(Item.id == contained_item_id).filter(Item.deleted_time == None).first()

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
            associations = ItemToItem.query.filter(ItemToItem.parent_id == item_id).options(joinedload('item')).all()
            return [e.item for e in associations]
        except IntegrityError as err:
            message = str(err)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('That item is already contained in this item. %s', err)
                abort(409, 'That item is already contained in this item.')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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

        # pylint: disable=C0121
        if Item.query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item (current) not found!')
        # pylint: disable=C0121
        if Item.query.filter(Item.id == contained_item_id).filter(Item.deleted_time == None).first() is None:
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


@ANS.route('/<int:item_id>/files/')
class ItemFile(Resource):
    """
    The files of a singe item
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_list_with(FILE_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get all files for this item.
        """
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        if base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first() is None:
            abort(404, 'Requested item not found!')

        return File.query.filter(File.item_id == item_id).options(joinedload('item')).all()

@ANS.route('/<int:item_id>/lending/')
class ItemLendings(Resource):
    """
    Current lending of a single item.
    """

    @jwt_required
    @ANS.response(404, 'Requested item not found!')
    @API.marshal_list_with(LENDING_GET)
    # pylint: disable=R0201
    def get(self, item_id):
        """
        Get the lending concerning the specific item.
        """
        base_query = Item.query

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                base_query = base_query.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                base_query = base_query.filter(Item.visible_for == 'all')

        # pylint: disable=C0121
        item = base_query.filter(Item.id == item_id).filter(Item.deleted_time == None).first()
        if item is None:
            abort(404, 'Requested item not found!')

        return item.lending
