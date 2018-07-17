"""
Authentication Providers
"""

from .. import APP
from . import ldap_auth_provider, basic_auth_provider

if APP.config.get('DEBUG', False):
    from . import debug_auth_provider
