"""
This module contains all api endpoints for the rules
"""
from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ... import DB, APP
from ..models import RULE_GET, RULE_POST, SUB_RULE_GET, SUB_RULE_POST
from ...login import UserRole
from ...db_models.ruleEngine import Rule, SubRule, KeyValueStore

PATH: str = '/rules/rule'
ANS = API.namespace('rule', description='The rule endpoints', path=PATH)


@ANS.route('/')
class RuleList(Resource):

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @API.marshal_list_with(RULE_GET)
    def get(self):
        return Rule.query.order_by(Rule.name).all()

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=RULE_GET, body=RULE_POST)
    @ANS.response(409, 'Name is not unique.')
    def post(self):
        new = Rule(**request.get_json())

        try:
            DB.session.add(new)
            DB.session.commit()
            return marshal(new, RULE_GET), 201
        except IntegrityError as err:
            message = str(err)
            print(message)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('Name is not unique. %s', err)
                abort(409, 'Name is not unique!')
            abort(500)


@ANS.route('/<int:rule_id>/')
class RuleDetail(Resource):
    """
    Single rule object
    """

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested rule was not found!')
    @API.marshal_with(RULE_GET)
    # pylint: disable=R0201
    def get(self, rule_id):
        """
        Get a single rule object
        """
        rule = Rule.query.order_by(Rule.name).first()

        if rule is None:
            APP.logger.debug('Requested rule (id: %s) not found!', type_id)
            abort(404, 'Requested rule not found!')

        return rule


@ANS.route('/<int:rule_id>/subrule')
class RuleSubRuleDetail(Resource):
    """
    Sub Rule Details
    """

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.doc(model=SUB_RULE_GET, body=SUB_RULE_POST)
    @ANS.response(409, 'Name is not unique.')
    def post(self, rule_id):
        """
        Add a new sub rule to a rule
        """
        variable = KeyValueStore.query.filter(
                KeyValueStore.key == request.get_json()['variable_key']).first()
        if variable is None:
            new_variable = KeyValueStore(request.get_json()['variable_key'])

            try:
                DB.session.add(new_variable)
                DB.session.commit()
            except IntegrityError as err:
                message = str(err)
                print(message)
                if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                    APP.logger.info('Name is not unique. %s', err)
                    abort(409, 'Name is not unique!')
                abort(500)

        new = SubRule(rule_id=rule_id, **request.get_json())

        try:
            DB.session.add(new)
            DB.session.commit()
            return marshal(new, SUB_RULE_GET), 201
        except IntegrityError as err:
            message = str(err)
            print(message)
            if APP.config['DB_UNIQUE_CONSTRAIN_FAIL'] in message:
                APP.logger.info('Name is not unique. %s', err)
                abort(409, 'Name is not unique!')
            abort(500)
