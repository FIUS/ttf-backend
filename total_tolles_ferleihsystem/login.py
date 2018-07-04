"""
Module for the authentication and user handling
"""

from enum import IntEnum
from typing import Dict, List, Union
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
    _login_provider: Union['LoginProvider', None]

    def __init__(self, name: str, login_provider: Union['LoginProvider', None] = None):
        self.name = name
        self._login_provider = login_provider


class LoginProvider(ABC):
    """
    Abstract class which allows the login service to lookup users.
    """

    __registered_providers__: Dict[str, 'LoginProvider'] = {}

    @staticmethod
    def registerProvider(name: str, login_provider: 'LoginProvider'):
        """
        Register an Instance of LoginProvider under given name.

        Arguments:
            name {str} -- Name of the LoginProvider
            login_provider {LoginProvider} -- LoginProvider Instance

        Raises:
            KeyError -- If name is already registered with a different LoginProvider
        """
        if name in LoginProvider.__registered_providers__:
            raise KeyError('Name already in use!')
        LoginProvider.__registered_providers__[name] = login_provider

    @staticmethod
    def getLoginProvider(name: str) -> Union['LoginProvider', None]:
        """
        Get a registered LoginProvider by its name.

        Arguments:
            name {str} -- Name of the LoginProvider

        Returns:
            Union[LoginProvider, None] -- LoginProvider or None
        """
        return LoginProvider.__registered_providers__.get(name)

    @staticmethod
    def listLoginProviders() -> List[str]:
        """
        Get a list of Registered names of LoginProviders.

        Returns:
            List[str] -- All registered names of LoginProviders.
        """

        return list(LoginProvider.__registered_providers__.keys())

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

    _login_providers: List[LoginProvider]

    def __init__(self, login_providers: List[str], anonymous_user: bool = True):
        self.anonymous_user = anonymous_user

        self._login_providers = []

        if login_providers:
            for name in login_providers:
                provider = LoginProvider.getLoginProvider(name)
                if provider:
                    provider.init()
                    self._login_providers.append(provider)

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
        for provider in self._login_providers:
            if provider.valid_user(user_id):
                user = User(user_id, provider)
                if provider.is_admin(user_id):
                    user.role = UserRole.ADMIN
                elif provider.is_moderator(user_id):
                    user.role = UserRole.MODERATOR
                return user
        return None

    def check_password(self, user: User, password: str) -> bool:
        """
        Check function for a password with an existing user object
        """

        if self.anonymous_user and user.name == self.ANONYMOUS_IDENTITY and password == '':
            return True

        provider = user._login_provider
        if provider:
            return provider.valid_password(user.name, password)

        return False
