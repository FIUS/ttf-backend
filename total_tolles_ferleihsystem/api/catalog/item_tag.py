"""
This module contains all API endpoints for the namespace 'item_tag'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ITEM_TAG_GET, ITEM_TAG_POST, ATTRIBUTE_DEFINITION_GET, ID, ITEM_TAG_PUT
from ... import db

from ...db_models.tag import Tag, TagToAttributeDefinition

PATH: str = '/catalog/item_tags'
ANS = api.namespace('item_tag', description='ItemTags', path=PATH)


@ANS.route('/')
class ItemTagList(Resource):
    """
    Item tags root element
    """

    @api.doc(security=None)
    @api.param('deleted', 'get all deleted elements (and only these)', type=bool, required=False, default=False)
    @api.marshal_list_with(ITEM_TAG_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all item tags currently in the system
        """
        test_for = request.args.get('deleted', 'false') == 'true'
        return Tag.query.filter(Tag.deleted == test_for).all()

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
        tag = Tag.query.filter(Tag.id == tag_id).first()

        return tag
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
    @ANS.response(204, 'Sucess.')
    @ANS.doc(body=ITEM_TAG_PUT)
    # pylint: disable=R0201
    def put(self, tag_id):
        """
        Updates the item tag object
        """
        item_tag = Tag.query.filter(Tag.id == tag_id).first()
        newInfo = request.get_json()
        item_tag.deleted = False

        if("name" in newInfo):
            item_tag.name = newInfo["name"]
        if("lending_duration" in newInfo):
            item_tag.lending_duration = newInfo["lending_duration"]
        if("visible_for" in newInfo):
            item_tag.visible_for = newInfo["visible_for"]
        db.session.commit()
        return "", 204


@ANS.route('/<int:tag_id>/attributes/')
class ItemTagAttributes(Resource):
    """
    The attributes of a single item tag element
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def get(self, tag_id):
        """
        Get all attribute definitions for this tag.
        """
       
       # Two possibilitys:
       # return [e.attribute_definition for e in TagToAttributeDefinition.query.filter(TagToAttributeDefinition.tag_id == tag_id).all()]
       # return  [e.attribute_definition for e in Tag.query.filter(Tag.id == tag_id).first()._tag_to_attribute_definitions ]
        associations = TagToAttributeDefinition.query.filter(TagToAttributeDefinition.tag_id == tag_id).all()
        return [e.attribute_definition for e in associations]

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_DEFINITION_GET)
    @ANS.doc(model=ATTRIBUTE_DEFINITION_GET, body=ID)
    @ANS.response(409, 'Attribute definition is already associated with this tag!')
    # pylint: disable=R0201
    def post(self,tag_id):
        """
        Associate a new attribute definition with the tag.
        """
        new = TagToAttributeDefinition(tag_id,request.get_json()["id"])
        try:
            db.session.add(new)
            db.session.commit()
            associations = TagToAttributeDefinition.query.filter(TagToAttributeDefinition.tag_id == tag_id).all()
            return [e.attribute_definition for e in associations]
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Attribute definition is already asociated with this tag!')
            abort(500)

    @api.doc(security=None)
    @ANS.doc(body=ID)
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self,tag_id):
        """
        Remove association of a attribute definition with the tag.
        """
        association = (TagToAttributeDefinition.query
                                               .filter(TagToAttributeDefinition.tag_id == tag_id)
                                               .filter(TagToAttributeDefinition.attribute_definition_id == request.get_json()["id"])
                                               .first())
        if association is None: 
            return '', 204
        try:
            db.session.delete(association)
            db.session.commit()
            return '', 204
        except IntegrityError:
            abort(500)
