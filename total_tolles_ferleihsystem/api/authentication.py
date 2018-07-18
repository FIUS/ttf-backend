"""
Model for all the available authentication endpoints
"""
from flask_restplus import Resource, fields, abort
from flask_jwt_extended import jwt_required, create_access_token, \
                               get_jwt_identity, create_refresh_token, \
                               get_jwt_claims, jwt_refresh_token_required

from . import API
from .models import AUTHENTICATION_ROUTES_MODEL
from .. import APP, AUTH_LOGGER

from ..login import LoginService, UserRole


ANS = API.namespace('auth', description='Authentication Resources:')

LOGIN_SERVICE: LoginService = LoginService(APP.config.get('LOGIN_PROVIDERS', []))

USER_AUTH_MODEL = API.model('UserAuth', {
    'username': fields.String(required=True, example='admin'),
    'password': fields.String(required=True, example='admin')
})

JWT_RESPONSE = API.model('JWT', {
    'access_token': fields.String(required=True)
})

JWT_RESPONSE_FULL = API.inherit('JWT_FULL', JWT_RESPONSE, {
    'refresh_token': fields.String(reqired=True)
})

CHECK_RESPONSE = API.model('check', {
    'username': fields.String(required=True, readonly=True),
    'role': fields.Integer(required=True, readonly=True)
})


def login_user():
    """
    Login a user.
    """

    username = API.payload.get('username', None)
    password = API.payload.get('password', None)
    user = LOGIN_SERVICE.get_user(username, password)

    if not user:
        AUTH_LOGGER.debug('Attempted login with invalid credentials with username "%s".', username)
        abort(401, 'Wrong username or pasword.')

    AUTH_LOGGER.info('New login from user "%s"', username)
    return user


@ANS.route('/')
class AuthenticationRoutes(Resource):
    """Authentication Routes Hal resource."""

    @API.doc(security=None)
    @API.marshal_with(AUTHENTICATION_ROUTES_MODEL)
    # pylint: disable=R0201
    def get(self):
        """Authentication root resource."""
        return

@ANS.route('/guest-login/')
class GuestLogin(Resource):
    """Login resource."""

    @API.doc(security=None)
    @API.marshal_with(JWT_RESPONSE_FULL)
    # pylint: disable=R0201
    def post(self):
        """Login as guest to get a new token and refresh token."""
        user = LOGIN_SERVICE.get_anonymous_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True),
            'refresh_token': create_refresh_token(identity=user)
        }
        return ret

@ANS.route('/login/')
class Login(Resource):
    """Login resource."""

    @API.doc(security=None)
    @API.expect(USER_AUTH_MODEL)
    @API.response(401, 'Wrong username or pasword.')
    @API.marshal_with(JWT_RESPONSE_FULL)
    # pylint: disable=R0201
    def post(self):
        """Login with username and password to get a new token and refresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True),
            'refresh_token': create_refresh_token(identity=user)
        }
        return ret


@ANS.route('/fresh-login/')
class FreshLogin(Resource):
    """Resource for a fresh login token without refresh token."""

    @API.doc(security=None)
    @API.expect(USER_AUTH_MODEL)
    @API.response(401, 'Wrong username or pasword.')
    @API.marshal_with(JWT_RESPONSE)
    # pylint: disable=R0201
    def post(self):
        """Login with username and password to get a fresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True)
        }
        return ret


@ANS.route('/check/')
class Check(Resource):
    """Resource to check access tokens."""

    @jwt_required
    @API.response(401, 'Not Authenticated')
    @API.marshal_with(CHECK_RESPONSE)
    # pylint: disable=R0201
    def get(self):
        """Check your current access token."""
        ret = {
            'username': get_jwt_identity(),
            'role': get_jwt_claims()
        }
        return ret


@ANS.route('/refresh/')
class Refresh(Resource):
    """Resource to refresh access tokens."""

    @API.doc(security=['jwt-refresh'])
    @jwt_refresh_token_required
    @API.response(401, 'Wrong username or pasword.')
    @API.marshal_with(JWT_RESPONSE)
    # pylint: disable=R0201
    def post(self):
        """Create a new access token with a refresh token."""
        username = get_jwt_identity()
        role = UserRole(get_jwt_claims())
        AUTH_LOGGER.debug('User "%s" asked for a new access token.', username)
        new_token = create_access_token(identity={
            'name': username,
            'role': role
        }, fresh=False)
        ret = {'access_token': new_token}
        return ret, 200
