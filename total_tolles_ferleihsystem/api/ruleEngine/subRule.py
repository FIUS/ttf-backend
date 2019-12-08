from flask import request
from flask_restplus import Resource, abort, marshal
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from .. import API, satisfies_role
from ... import DB, APP
from ..models import SUB_RULE_GET, SUB_RULE_POST
from ...login import UserRole
from ...db_models.ruleEngine import SubRule, KeyValueStore

PATH: str = '/rules/subrule'
ANS = API.namespace('subrule', description='The subrule endpoints', path=PATH)


@ANS.route('/')
class SubRuleList(Resource):

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @API.marshal_list_with(SUB_RULE_GET)
    def get(self):
        return SubRule.query.order_by(SubRule.rule_id).order_by(SubRule.position).all()


@ANS.route('/<int:sub_rule_id>/')
class SubRuleDetail(Resource):
    """
    Single sub rule object
    """

    @jwt_required
    @satisfies_role(UserRole.ADMIN)
    @ANS.response(404, 'Requested sub rule was not found!')
    @API.marshal_with(SUB_RULE_GET)
    # pylint: disable=R0201
    def get(self, sub_rule_id):
        """
        Get a single sub rule object
        """
        subRule = SubRule.query.filter(SubRule.id == sub_rule_id).first()

        if subRule is None:
            APP.logger.debug('Requested sub rule (id: %s) not found!', type_id)
            abort(404, 'Requested sub rule not found!')

        return subRule
