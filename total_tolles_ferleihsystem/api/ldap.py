"""Module for ldap communication etc."""

from enum import Enum, auto


class UserRole(Enum):
    GUEST = auto
    MODERATOR = auto
    ADMIN = auto


class User():

    username: str
    role: UserRole = UserRole.GUEST
