"""
This module contains all API endpoints for the namespace 'item_tag'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ..models import ITEM_TAG_GET, ITEM_TAG_POST, ATTRIBUTE_DEFINITION_GET, ID, ITEM_TAG_PUT
from ... import DB
from ...login import UserRole

from ...db_models.tag import Tag, TagToAttributeDefinition
from ...db_models.attributeDefinition import AttributeDefinition

PATH: str = '/catalog/item_tags'
ANS = API.namespace('item_tag', description='ItemTags', path=PATH)


@ANS.route('/')
class ItemTagList(Resource):
    """
    Item tags root item tag
    """

    @jwt_required
    @API.param('deleted', 'get all deleted item tags (and only these)', type=bool, required=False, default=False)
    @API.marshal_list_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item tags currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return Tag.query.filter(Tag.deleted == test_for).order_by(Tag.name).all()

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
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
            DB.session.add(new)
            DB.session.commit()
            return marshal(new, ITEM_TAG_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:tag_id>/')
class ItemTagDetail(Resource):
    """
    Single item tag object
    """

    @jwt_required
    @ANS.response(404, 'Requested item tag not found!')
    @API.marshal_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self, tag_id):
        """
        Get a single item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        if item_tag is None:
            abort(404, 'Requested item tag not found!')
        return item_tag

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item tag not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, tag_id):
        """
        Delete a item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        if item_tag is None:
            abort(404, 'Requested item tag not found!')
        item_tag.deleted = True
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested item tag not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def post(self, tag_id):
        """
        Undelete a item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        if item_tag is None:
            abort(404, 'Requested item tag not found!')
        item_tag.deleted = False
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=ITEM_TAG_GET, body=ITEM_TAG_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Requested item tag not found!')
    # pylint: disable=R0201
    def put(self, tag_id):
        """
        Replace a item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        if item_tag is None:
            abort(404, 'Requested item tag not found!')
        item_tag.update(**request.get_json())
        try:
            DB.session.commit()
            return marshal(item_tag, ITEM_TAG_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)



@ANS.route('/<int:tag_id>/attributes/')
class ItemTagAttributes(Resource):
    """
    The attributes of a single item tag object
    """

    @jwt_required
    @ANS.response(404, 'Requested item tag not found!')
    @API.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def get(self, tag_id):
        """
        Get all attribute definitions for this tag.
        """
        if Tag.query.filter(Tag.id == tag_id).first() is None:
            abort(404, 'Requested item tag not found!')
       # Two possibilitys:
       # return [e.attribute_definition for e in TagToAttributeDefinition.query
       # .filter(TagToAttributeDefinition.tag_id == tag_id).all()]
       # return  [e.attribute_definition for e in Tag.query.filter(Tag.id == tag_id)
       # .first()._tag_to_attribute_definitions ]
        associations = TagToAttributeDefinition.query.filter(TagToAttributeDefinition.tag_id == tag_id).all()
        return [e.attribute_definition for e in associations]

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=ATTRIBUTE_DEFINITION_GET, body=ID)
    @ANS.response(404, 'Requested item tag not found!')
    @ANS.response(400, 'Requested attribute definition not found!')
    @ANS.response(409, 'Attribute definition is already associated with this tag!')
    @API.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def post(self, tag_id):
        """
        Associate a new attribute definition with the tag.
        """
        attribute_definition_id = request.get_json()["id"]

        if Tag.query.filter(Tag.id == tag_id).first() is None:
            abort(404, 'Requested item tag not found!')
        if AttributeDefinition.query.filter(AttributeDefinition.id == attribute_definition_id).first() is None:
            abort(400, 'Requested attribute definition not found!')

        new = TagToAttributeDefinition(tag_id, attribute_definition_id)
        try:
            DB.session.add(new)
            DB.session.commit()
            associations = TagToAttributeDefinition.query.filter(TagToAttributeDefinition.tag_id == tag_id).all()
            return [e.attribute_definition for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Attribute definition is already asociated with this tag!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(body=ID)
    @ANS.response(404, 'Requested item tag not found!')
    @ANS.response(400, 'Requested attribute definition not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, tag_id):
        """
        Remove association of a attribute definition with the tag.
        """
        attribute_definition_id = request.get_json()["id"]

        if Tag.query.filter(Tag.id == tag_id).first() is None:
            abort(404, 'Requested item tag not found!')
        if AttributeDefinition.query.filter(AttributeDefinition.id == attribute_definition_id).first() is None:
            abort(400, 'Requested attribute definition not found!')
        association = (TagToAttributeDefinition
                       .query
                       .filter(TagToAttributeDefinition.tag_id == tag_id)
                       .filter(TagToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                       .first())
        if association is None:
            return '', 204
        try:
            DB.session.delete(association)
            DB.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)
