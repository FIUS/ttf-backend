"""
This module contains all API endpoints for the namespace 'lending'
"""


from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from . import API, satisfies_role
from .. import DB

from .models import LENDING_GET, LENDING_POST, LENDING_PUT, ID_LIST
from ..login import UserRole
from ..db_models.item import Lending, ItemToLending, Item

PATH: str = '/lending'
ANS = API.namespace('lending', description='Lendings', path=PATH)

@ANS.route('/')
class LendingList(Resource):
    """
    Lendings root item tag
    """

    @jwt_required
    @API.marshal_list_with(LENDING_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all lendings currently in the system
        """
        return Lending.query.all()

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=LENDING_GET, body=LENDING_POST)
    @ANS.response(201, 'Created.')
    @ANS.response(400, "Item not found")
    @ANS.response(400, "Item not lendable")
    @ANS.response(400, "Item already lended")
    # pylint: disable=R0201
    def post(self):
        """
        Add a new lending to the system
        """
        json = request.get_json()
        item_ids = json.pop('item_ids')
        items = []
        item_to_lendings = []

        for element in item_ids:
            item = Item.query.filter(Item.id == element).first()
            if item is None:
                abort(400, "Item not found:" + str(element))
            if not item.type.lendable:
                abort(400, "Item not lendable:" + str(element))
            if item.is_currently_lended:
                abort(400, "Item already lended:" + str(element))
            items.append(item)

        new = Lending(**json)
        try:
            DB.session.add(new)
            DB.session.commit()
            for element in items:
                item_to_lendings.append(ItemToLending(element, new))
            DB.session.add_all(item_to_lendings)
            DB.session.commit()
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

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.response(404, 'Requested lending not found!')
    @API.marshal_with(LENDING_GET)
    # pylint: disable=R0201
    def get(self, lending_id):
        """
        Get a single lending object
        """
        lending = Lending.query.filter(Lending.id == lending_id).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        return lending

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
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
        DB.session.delete(lending)
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
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

        json = request.get_json()
        item_ids = json.pop('item_ids')
        items = []
        item_to_lendings = []

        for element in item_ids:
            item = Item.query.filter(Item.id == element).first()
            if item is None:
                abort(400, "Item not found:" + str(element))
            if not item.type.lendable:
                abort(400, "Item not lendable:" + str(element))
            if item.is_currently_lended:
                abort(400, "Item already lended:" + str(element))
            items.append(item)

        lending.update(**request.get_json())
        try:
            DB.session.commit()
            for element in ItemToLending.query.filter(ItemToLending.lending_id == lending_id).all():
                DB.session.delete(element)
            for element in items:
                item_to_lendings.append(ItemToLending(element, lending))
            DB.session.add_all(item_to_lendings)
            DB.session.commit()
            return marshal(lending, LENDING_GET), 200
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500)

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=LENDING_GET, body=ID_LIST)
    @ANS.response(404, 'Requested lending not found!')
    @ANS.response(400, 'Requested item is not part of this lending.')
    @API.marshal_with(LENDING_GET)
    # pylint: disable=R0201
    def post(self, lending_id):
        """
        Give back a list of items.
        """
        lending = Lending.query.filter(Lending.id == lending_id).first()
        if lending is None:
            abort(404, 'Requested lending not found!')

        ids = request.get_json()["ids"]
        try:
            for element in ids:
                to_delete = ItemToLending.query.filter(ItemToLending.item_id == element).first()
                if to_delete is None:
                    abort(400, "Requested item is not part of this lending:" + str(element))
                DB.session.delete(to_delete)
            DB.session.commit()
            return lending
        except IntegrityError:
            abort(500)
