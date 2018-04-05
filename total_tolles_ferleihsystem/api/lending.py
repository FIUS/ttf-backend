"""
This module contains all API endpoints for the namespace 'lending'
"""


from flask import request
from flask_restplus import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError

from . import api as api
from .. import db

from .models import LENDING_GET, LENDING_POST, LENDING_PUT
from ..db_models.item import Lending, ItemToLending, Item

PATH: str = '/lending'
ANS = api.namespace('lending', description='Lendings', path=PATH)

@ANS.route('/')
class LendingList(Resource):
    """
    Lendings root item tag
    """

    @api.doc(security=None)
    @api.marshal_list_with(LENDING_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all lendings currently in the system
        """
        return Lending.query.all()

    @api.doc(security=None)
    @ANS.doc(model=LENDING_GET, body=LENDING_POST)
    @ANS.response(201, 'Created.')
    @ANS.response(400, "Item not found")
    # pylint: disable=R0201
    def post(self):
        """
        Add a new lending to the system
        """
        json = request.get_json()
        item_ids = json.pop('items')
        items = []
        item_to_lendings = []

        for element in item_ids:
            item = Item.query.filter(Item.id == element).first()
            if item is None:
                abort(400, "Item not found:" + str(element))
            items.append(item)

        new = Lending(**json)
        try:
            db.session.add(new)
            db.session.commit()
            for element in items:
                item_to_lendings.append(ItemToLending(element, new))
            db.session.add_all(item_to_lendings)
            db.session.commit()
            return marshal(new, LENDING_GET), 201
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

@ANS.route('/<int:lending_id>/')
class LendingDetail(Resource):
    """
    Single lending object
    """

    @api.doc(security=None)
    @api.marshal_with(LENDING_GET)
    @ANS.response(404, 'Requested lending not found!')
    # pylint: disable=R0201
    def get(self, lending_id):
        """
        Get a single lending object
        """
        lending = Lending.query.filter(Lending.id == lending_id).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        return lending
   
    @ANS.response(404, 'Requested lending not found!')
    @ANS.response(204, 'Success.')
    # pylint: disable=R0201
    def delete(self, lending_id):
        """
        Delete a lending object
        """
        lending = Lending.query.filter(Lending.id == lending_id).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        db.session.delete(lending)
        db.session.commit()
        return "", 204
    
    @ANS.doc(model=LENDING_GET, body=LENDING_PUT)
    @ANS.response(409, 'Name is not Unique.')
    @ANS.response(404, 'Requested lending not found!')
    # pylint: disable=R0201
    def put(self, lending_id):
        """
        Replace a lending object
        """
        lending = Lending.query.filter(Lending.id == lending_id).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        lending.update(**request.get_json())
        try:
            db.session.commit()
            return marshal(lending, LENDING_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)