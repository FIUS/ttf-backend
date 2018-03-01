from flask import url_for, request
from flask_restplus import Resource, fields, abort
from flask_jwt_extended import jwt_required, create_access_token, \
                               get_jwt_identity, create_refresh_token, \
                               get_jwt_claims, jwt_refresh_token_required

from . import api as api
from .import auth_logger
from .. import jwt
from .. import app

from ..login import User, UserRole, LoginService, BasicAuthProvider


ns = api.namespace('auth', description='Authentication Resources:')

login_service: LoginService
if app.config['DEBUG']:
    login_service = LoginService(BasicAuthProvider())
else:
    #FIXME add LDAP auth provider here
    login_service = LoginService(None)

user_auth_model = api.model('UserAuth', {
    'username': fields.String(required=True, example='admin'),
    'password': fields.String(required=True, example='admin')
})

jwt_response = api.model('JWT', {
    'access_token': fields.String(required=True)
})

jwt_response_full = api.inherit('JWT_FULL', jwt_response, {
    'refresh_token': fields.String(reqired=True)
})

check_response = api.model('check', {
    'username': fields.String(required=True),
    'role': fields.String()
})


def login_user():
    """Login a user."""
    username = api.payload.get('username', None)
    password = api.payload.get('password', None)
    user = login_service.get_user_by_id(username)
    if not user:
        auth_logger.debug('Attempted login with unknown username "%s".', username)
        abort(401, 'Wrong username or pasword.')
    if not login_service.check_password(user, password):
        auth_logger.error('Attempted login with invalid password for user "%s"', username)
        abort(401, 'Wrong username or pasword.')

    auth_logger.info('New login from user "%s"', username)
    return user


@ns.route('/')
class Authenticate(Resource):
    """Login resource."""

    @api.doc(security=None)
    @api.marshal_with(jwt_response_full)
    @api.response(401, 'Wrong username or pasword.')
    @api.expect(user_auth_model)
    def post(self):
        """Login with username and password to get a new token and refresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True),
            'refresh_token': create_refresh_token(identity=user)
        }
        return ret


@ns.route('/fresh-login/')
class FrechLogin(Resource):
    """Resource for a fresh login token without refresh token."""

    @api.doc(security=None)
    @api.marshal_with(jwt_response)
    @api.response(401, 'Wrong username or pasword.')
    @api.expect(user_auth_model)
    def post(self):
        """Login with username and password to get a fresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True)
        }
        return ret


@ns.route('/check/')
class Check(Resource):
    """Resource to check access tokens."""

    @api.marshal_with(check_response)
    @api.response(401, 'Not Authenticated')
    @jwt_required
    def get(self):
        """Check your current access token."""
        ret = {
            'username': get_jwt_identity(),
            'role': get_jwt_claims()
        }
        return ret


@ns.route('/refresh/')
class Refresh(Resource):
    """Resource to refresh access tokens."""

    @api.doc(security=['jwt-refresh'])
    @api.marshal_with(jwt_response)
    @api.response(401, 'Wrong username or pasword.')
    @jwt_refresh_token_required
    def post(self):
        """Create a new access token with a refresh token."""
        username = get_jwt_identity()
        user = login_service.get_user_by_id(username)
        if not user:
            abort(401, "User doesn't exist.")
        auth_logger.debug('User "%s" asked for a new access token.', username)
        new_token = create_access_token(identity=user, fresh=False)
        ret = {'access_token': new_token}
        return ret, 200
