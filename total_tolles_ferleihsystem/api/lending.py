"""
This module contains all API endpoints for the namespace 'lending'
"""


from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from . import API, satisfies_role
from .. import DB

from .models import LENDING_GET, LENDING_POST, LENDING_PUT, ID_LIST
from ..login import UserRole
from ..db_models.item import Lending, Item

PATH: str = '/lending'
ANS = API.namespace('lending', description='Lendings', path=PATH)

@ANS.route('/')
class LendingList(Resource):
    """
    List of all active lendings
    """

    @jwt_required
    @API.marshal_list_with(LENDING_GET)
    # pylint: disable=R0201
    def get(self):
        """
        Get a list of all lendings currently in the system
        """

        return Lending.query.options(joinedload('_items')).all()

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=LENDING_GET, body=LENDING_POST)
    @ANS.response(201, 'Created.')
    @ANS.response(400, "Item not found")
    @ANS.response(400, "Item not lendable")
    @ANS.response(400, "Item already lent")
    # pylint: disable=R0201
    def post(self):
        """
        Add a new lending to the system
        """
        try:
            new = Lending(** request.get_json())
        except ValueError as err:
            abort(400, str(err))
        
        DB.session.add(new)
        DB.session.commit()
        return marshal(new, LENDING_GET), 201

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
        lending = Lending.query.filter(Lending.id == lending_id).options(joinedload('_items')).first()
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
        lending.pre_delete()
        DB.session.delete(lending)
        DB.session.commit()
        return "", 204

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(model=LENDING_GET, body=LENDING_PUT)
    @ANS.response(404, 'Requested lending not found!')
    @ANS.response(400, "Item not found")
    @ANS.response(400, "Item not lendable")
    @ANS.response(400, "Item already lent")
    # pylint: disable=R0201
    def put(self, lending_id):
        """
        Replace a lending object
        """
        lending = Lending.query.filter(Lending.id == lending_id).options(joinedload('_items')).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        try:
            lending.update(**request.get_json())
        except ValueError as err:
            abort(400, str(err))

        DB.session.commit()
        return marshal(lending, LENDING_GET), 200

    @jwt_required
    @satisfies_role(UserRole.MODERATOR)
    @ANS.doc(body=ID_LIST)
    @ANS.response(404, 'Requested lending not found!')
    @ANS.response(400, "Item not found")
    @ANS.response(201, "Lending would be empty. Was deleted.")
    # pylint: disable=R0201
    def post(self, lending_id):
        """
        Give back a list of items.
        """
        lending = Lending.query.filter(Lending.id == lending_id).options(joinedload('_items')).first()
        if lending is None:
            abort(404, 'Requested lending not found!')
        try:
            lending.remove_items(request.get_json()["ids"])
        except ValueError as err:
            abort(400, str(err))
        DB.session.commit()
        if len(lending._items) <= 0: 
            lending.pre_delete()
            DB.session.delete(lending)
            DB.session.commit()
            return None, 201
        return marshal(lending, LENDING_GET)
