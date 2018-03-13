"""
Module for the authentication and user handling
"""

from enum import IntEnum
from typing import Dict, List
from abc import ABC, abstractmethod


class UserRole(IntEnum):
    """
    This Enum describes the possible rights / access levels to the software.
    """

    GUEST = 0
    MODERATOR = 1
    ADMIN = 2

# pylint: disable=R0903
class User():
    """
    This Class represents a user in the system.
    """

    name: str
    role: UserRole = UserRole.GUEST

    def __init__(self, name: str):
        self.name = name


class LoginProvider(ABC):
    """
    Abstract class which allows the login service to lookup users.
    """

    @abstractmethod
    def init(self) -> None:
        """
        Init function which is called when the LoginProvider is connected to a
        LoginService.
        """
        pass

    @abstractmethod
    def valid_user(self, user_id: str) -> bool:
        """
        Check function to check if a user exists
        """
        pass

    @abstractmethod
    def valid_password(self, user_id: str, password: str) -> bool:
        """
        Check function if a user id and password are valid
        """
        pass

    @abstractmethod
    def is_admin(self, user_id: str) -> bool:
        """
        Check function if a user has admin privilages
        """
        pass

    @abstractmethod
    def is_moderator(self, user_id: str) -> bool:
        """
        Check function if a user has moderator privilages
        """
        pass


class LoginService():
    """
    This class handles the actual login with the help of a valid login provider.
    """

    ANONYMOUS_IDENTITY: str = 'anonymous'

    anonymous_user: bool

    _login_provider: LoginProvider

    def __init__(self, loginProvider: LoginProvider, anonymous_user: bool = True):
        self.anonymous_user = anonymous_user

        self._login_provider = loginProvider
        self._login_provider.init()

    def get_login_provider(self) -> LoginProvider:
        """
        Getter function for the connected login provider
        """
        return self._login_provider

    def get_anonymous_user(self) -> User:
        """
        Getter function for the anonymous user. This will return None
        anonymous_user is deactivated.
        """

        if self.anonymous_user:
            return User(self.ANONYMOUS_IDENTITY)
        return None

    def get_user_by_id(self, user_id: str) -> User:
        """
        Getter for a user object by the user_id
        """

        if self.anonymous_user and user_id == self.ANONYMOUS_IDENTITY:
            return self.get_anonymous_user()
        if not self._login_provider.valid_user(user_id):
            return None

        user = User(user_id)
        if self._login_provider.is_admin(user_id):
            user.role = UserRole.ADMIN
        elif self._login_provider.is_moderator(user_id):
            user.role = UserRole.MODERATOR
        return user

    def check_password(self, user: User, password: str) -> bool:
        """
        Check function for a password with an existing user object
        """

        if self.anonymous_user and user.name == self.ANONYMOUS_IDENTITY and password == '':
            return True

        return self._login_provider.valid_password(user.name, password)


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
