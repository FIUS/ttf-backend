"""
Auth Providers which provides LDAP login
"""

from ..login import LoginProvider
from .. import APP

from ldap3 import Connection


class LDAPAuthProvider(LoginProvider, name="LDAP"):
    """
    Example Login Provider with hardcoded insecure accounts.
    """

    def __init__(self):
        pass

    def init(self) -> None:
        pass

    def valid_user(self, user_id: str) -> bool:
        return None

    def valid_password(self, user_id: str, password: str) -> bool:
        return False

    def is_admin(self, user_id: str) -> bool:
        return False

    def is_moderator(self, user_id: str) -> bool:
        return False
