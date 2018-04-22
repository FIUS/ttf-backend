from logging import Formatter, Logger, DEBUG
from logging.handlers import RotatingFileHandler
from os import path
from functools import wraps
from typing import List
from flask import Blueprint, logging
from flask_restplus import Api, abort
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from .. import app, JWT
from ..login import User, UserRole


authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Standard JWT access token.'
    },
    'jwt-refresh': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT refresh token.'
    }
}


def satisfies_role(role: UserRole):
    """
    Check if the requesting user has one of the given roles.

    Must be applied after jwt_required decorator!
    """
    def has_roles_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role_claims = get_jwt_claims()
            if role > role_claims:
                auth_logger.debug('Access to ressource with isufficient rights. User role: %s, required role: %s',
                                  UserRole(role_claims), role)
                abort(403, 'Only users with {} privileges have access to this resource.'.format(role.name))
            else:
                return f(*args, **kwargs)
        return wrapper
    return has_roles_decorator


auth_logger = logging.create_logger(app)  # type: Logger

formatter = Formatter(fmt=app.config['AUTH_LOG_FORMAT'])

fh = RotatingFileHandler(path.join(app.config['LOG_PATH'], 'ttf_auth.log'),
                         maxBytes=104857600, backupCount=10)

fh.setFormatter(formatter)

fh.setLevel(DEBUG)

auth_logger.addHandler(fh)


api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint, version='0.1', title='TTF API', doc='/doc/',
          authorizations=authorizations, security='jwt',
          description='API for TTF.')


@JWT.user_identity_loader
def load_user_identity(user: User):
    return user.name


@JWT.user_claims_loader
def load_user_claims(user: User):
    return user.role.value


@JWT.expired_token_loader
def expired_token():
    message = 'Token is expired.'
    log_unauthorized(message)
    abort(401, message)


@JWT.invalid_token_loader
def invalid_token(message: str):
    log_unauthorized(message)
    abort(401, message)


@JWT.unauthorized_loader
def unauthorized(message: str):
    log_unauthorized(message)
    abort(401, message)


@JWT.needs_fresh_token_loader
def stale_token():
    message = 'The JWT Token is not fresh. Please request a new Token directly with the /auth resource.'
    log_unauthorized(message)
    abort(403, message)


@JWT.revoked_token_loader
def revoked_token():
    message = 'The Token has been revoked.'
    log_unauthorized(message)
    abort(401, message)


@api.errorhandler(NoAuthorizationError)
def missing_header(error):
    log_unauthorized(error.message)
    return {'message': error.message}, 401


def log_unauthorized(message):
    auth_logger.debug('Unauthorized access: %s', message)


from . import root, authentication, catalog, lending, search

app.register_blueprint(api_blueprint, url_prefix='/api')
