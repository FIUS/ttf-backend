from flask import url_for, request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy.exc import IntegrityError

from . import api as api
from .models import item_type_get, item_type_post
from .. import jwt, db

from ..db_models.itemType import ItemType

PATH: str= '/catalog/item_types'
ns = api.namespace('item_type', description='ItemTypes', path=PATH)


@ns.route('/')
class ItemTypeList(Resource):
    """Authentication Routes Hal resource."""

    @api.doc(security=None)
    @api.marshal_list_with(item_type_get)
    def get(self):
        return ItemType.query.all()

    @api.doc(security=None)
    @ns.doc(model=item_type_get, body=item_type_post)
    @ns.response(409, 'Name is not Unique.')
    def post(self):
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

@ns.route('/<int:id>/')
class ItemTypeDetail(Resource):

    @api.doc(security=None)
    @api.marshal_with(item_type_get)
    def get(self, id):
        return ItemType.query.filter(ItemType.id == id).first()
    
    @ns.response(404, 'Item type not found.')
    def delete(self, id):
        item_type = ItemType.get_by_id(id)
        if item_type is None:
            abort(404, 'Requested item type was not found!')
        db.session.delete(item_type)
        db.session.commit()
