"""
Auth Provider which provides three simple hardcoded logins for debugging purposes.
"""

from typing import Dict, List
from ..login import LoginProvider
from .. import APP

class BasicAuthProvider(LoginProvider, provider_name="Basic"):
    """
    Example Login Provider with hardcoded insecure accounts.
    """

    ACCOUNTS: Dict[str, str] = {
        'admin': APP.config['BASIC_AUTH_ADMIN_PASS'],
        'mod':   APP.config['BASIC_AUTH_MOD_PASS'],
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
        print('Admin Pass: ' + APP.config['BASIC_AUTH_ADMIN_PASS'])
        print('Mod Pass: ' + APP.config['BASIC_AUTH_MOD_PASS'])

    def valid_user(self, user_id: str) -> bool:
        return user_id in self.ACCOUNTS

    def valid_password(self, user_id: str, password: str) -> bool:
        return self.ACCOUNTS[user_id] == password

    def is_admin(self, user_id: str) -> bool:
        return user_id in self.ADMINS

    def is_moderator(self, user_id: str) -> bool:
        return user_id in self.MODS
