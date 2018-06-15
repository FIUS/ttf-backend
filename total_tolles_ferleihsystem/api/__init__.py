"""
Main API Module
"""
from logging import Formatter, Logger, getLogger, DEBUG
from logging.handlers import RotatingFileHandler
from os import path
from functools import wraps
from typing import List
from flask import Blueprint, logging
from flask_restplus import Api, abort
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from .. import APP, JWT
from ..login import User, UserRole


AUTHORIZATIONS = {
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
    def has_roles_decorator(func):
        """
        Decorator function
        """
        @wraps(func)
        # pylint: disable=R1710
        def wrapper(*args, **kwargs):
            """
            Wrapper function
            """
            role_claims = get_jwt_claims()
            if role > role_claims:
                AUTH_LOGGER.debug('Access to ressource with isufficient rights. User role: %s, required role: %s',
                                  UserRole(role_claims), role)
                abort(403, 'Only users with {} privileges have access to this resource.'.format(role.name))
            else:
                return func(*args, **kwargs)
        return wrapper
    return has_roles_decorator


AUTH_LOGGER = getLogger(APP.logger_name + '.auth')  # type: Logger

FORMATTER = Formatter(fmt=APP.config['AUTH_LOG_FORMAT'])

FH = RotatingFileHandler(path.join(APP.config['LOG_PATH'], 'ttf_auth.log'),
                         maxBytes=104857600, backupCount=10)

FH.setFormatter(FORMATTER)

FH.setLevel(DEBUG)

AUTH_LOGGER.addHandler(FH)


API_BLUEPRINT = Blueprint('api', __name__)

API = Api(API_BLUEPRINT, version='0.1', title='TTF API', doc='/doc/',
          authorizations=AUTHORIZATIONS, security='jwt',
          description='API for TTF.')


@JWT.user_identity_loader
def load_user_identity(user: User):
    """
    Loader for the user identity
    """
    return user.name


@JWT.user_claims_loader
def load_user_claims(user: User):
    """
    Loader for the user claims
    """
    return user.role.value


@JWT.expired_token_loader
def expired_token():
    """
    Handler function for a expired token
    """
    message = 'Token is expired.'
    log_unauthorized(message)
    abort(401, message)


@JWT.invalid_token_loader
def invalid_token(message: str):
    """
    Handler function for a invalid token
    """
    log_unauthorized(message)
    abort(401, message)


@JWT.unauthorized_loader
def unauthorized(message: str):
    """
    Handler function for a unauthorized api access
    """
    log_unauthorized(message)
    abort(401, message)


@JWT.needs_fresh_token_loader
def stale_token():
    """
    Handler function for a no more fresh token
    """
    message = 'The JWT Token is not fresh. Please request a new Token directly with the /auth resource.'
    log_unauthorized(message)
    abort(403, message)


@JWT.revoked_token_loader
def revoked_token():
    """
    Handler function for a revoked or invalid token
    """
    message = 'The Token has been revoked.'
    log_unauthorized(message)
    abort(401, message)


@API.errorhandler(NoAuthorizationError)
def missing_header(error):
    """
    Handler function for a NoAuthorizationError
    """
    log_unauthorized(error.message)
    return {'message': error.message}, 401


def log_unauthorized(message):
    """
    Logs unauthorized access
    """
    AUTH_LOGGER.debug('Unauthorized access: %s', message)

# pylint: disable=C0413
from . import root, authentication, catalog, lending, search, tasks

APP.register_blueprint(API_BLUEPRINT, url_prefix='/api')
