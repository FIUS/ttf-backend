"""
This module contains all API endpoints for the namespace 'attribute_definition'
"""

from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from .. import api as api
from ..models import ATTRIBUTE_DEFINITION_GET, ATTRIBUTE_DEFINITION_POST, ATTRIBUTE_DEFINITION_GET_ALL
from ... import db

from ...db_models.attribute import AttributeDefinition

PATH: str = '/catalog/attribute_definitions'
ANS = api.namespace('attribute_definition', description='The attribute definitions', path=PATH)


@ANS.route('/')
class ItemTags(Resource):
    """
    Attribute definitions root element
    """

    @api.doc(security=None)
    @api.marshal_list_with(ATTRIBUTE_DEFINITION_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all attribute definitions currently in the system
        """
        return AttributeDefinition.query.filter(AttributeDefinition.deleted == False).all()

    @api.doc(security=None)
    @ANS.doc(model=ATTRIBUTE_DEFINITION_GET, body=ATTRIBUTE_DEFINITION_POST)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(201, 'Created.')
    # pylint: disable=R0201
    def post(self):
        """
        Add a new attribute definition to the system
        """
        new = AttributeDefinition(**request.get_json())
        try:
            db.session.add(new)
            db.session.commit()
            return marshal(new, ATTRIBUTE_DEFINITION_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:definition_id>/')
class ItemTagDetail(Resource):
    """
    Single attribute definition element
    """

    @api.doc(security=None)
    @api.marshal_with(ATTRIBUTE_DEFINITION_GET_ALL)
    # pylint: disable=R0201
    def get(self, definition_id):
        """
        Get a single attribute definition
        """
        return AttributeDefinition.query.filter(AttributeDefinition.id == definition_id).first()

    @ANS.response(404, 'Attribute definition not found.')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, definition_id):
        """
        Delete a attribute definition
        """
        definition = AttributeDefinition.query.filter(AttributeDefinition.id == definition_id).first()
        if definition is None:
            abort(404, 'Requested item tag was not found!')
        definition.deleted = True
        db.session.commit()
        return "", 204