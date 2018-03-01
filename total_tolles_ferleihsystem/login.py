"""Module for the authentication handling etc."""

from enum import IntEnum
from typing import Dict, List
from abc import ABC, abstractclassmethod


class UserRole(IntEnum):
    GUEST = 0
    MODERATOR = 1
    ADMIN = 2


class User():

    username: str
    role: UserRole = UserRole.GUEST

    def __init__(self, username: str):
        self.username = username


class LoginProvider(ABC):

    @abstractclassmethod
    def init(self) -> None:
        pass

    @abstractclassmethod
    def valid_user(self, id: str) -> bool:
        pass

    @abstractclassmethod
    def valid_password(self, id: str, password: str) -> bool:
        pass

    @abstractclassmethod
    def is_admin(self, id: str) -> bool:
        pass

    @abstractclassmethod
    def is_moderator(self, id: str) -> bool:
        pass


class LoginService():

    _login_provider: LoginProvider

    def __init__(self, loginProvider: LoginProvider):
        self._login_provider = loginProvider
        self._login_provider.init()

    def get_login_provider(self) -> LoginProvider:
        return self._login_provider

    def get_user_by_id(self, id: str) -> User:
        if not self._login_provider.valid_user(id):
            return None

        user = User(id)

        if self._login_provider.is_admin(id):
            user.role = UserRole.ADMIN
        elif self._login_provider.is_moderator(id):
            user.role = UserRole.MODERATOR

        return user

    def check_password(self, user: User, password: str) -> bool:
        return self._login_provider.valid_password(user.username, password)


class BasicAuthProvider(LoginProvider):

    _authDB: Dict[str, str] = {
        'admin': 'admin',
        'mod':   'mod',
        'guest': 'guest'
    }

    _admin: List[str] = [
        'admin'
    ]

    _mod: List[str] = [
        'mod'
    ]

    def __init__(self):
        pass

    def init(self) -> None:
        pass

    def valid_user(self, id: str) -> bool:
        return id in self._authDB

    def valid_password(self, id: str, password: str) -> bool:
        return self._authDB[id] == password

    def is_admin(self, id: str) -> bool:
        return id in self._admin

    def is_moderator(self, id: str) -> bool:
        return id in self._mod
