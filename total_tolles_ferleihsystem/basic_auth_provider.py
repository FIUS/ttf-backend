from .login import LoginProvider
from . import APP

from typing import Dict, List


class BasicAuthProvider(LoginProvider):
    """
    Example Login Provider with hardcoded insecure accounts.
    """

    ACCOUNTS: Dict[str, str] = {
        'admin': 'admin',
        'mod':   'mod',
        'guest': 'guest'
    }
    ADMINS: List[str] = [
        'admin'
    ]
    MODS: List[str] = [
        'mod'
    ]

    def __init__(self):
        pass

    def init(self) -> None:
        pass

    def valid_user(self, user_id: str) -> bool:
        return user_id in self.ACCOUNTS

    def valid_password(self, user_id: str, password: str) -> bool:
        return self.ACCOUNTS[user_id] == password

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.ADMINS

    def is_moderator(self, user_id: str) -> bool:
        return user_id in self.MODS


if APP.config.get('DEBUG', False):
    LoginProvider.registerProvider('BasicAuthProvider', BasicAuthProvider())
