from .. import DB
from . import STD_STRING_SIZE
from hashlib import sha3_256


__all__=['Settings', ]

class Settings (DB.Model):

    __tablename__ = 'Settings'

    user = DB.Column(DB.String(STD_STRING_SIZE), primary_key=True, index=True)
    settings = DB.Column(DB.Text, nullable=True)

    def __init__(self, user: str, settings: str = '{}'):
        self.user = self._hash_user(user)
        self.settings = settings

    @staticmethod
    def _hash_user(user: str) -> str:
        hash_string = sha3_256(user.encode()).hexdigest()
        if len(hash_string) > STD_STRING_SIZE:
            return hash_string[:STD_STRING_SIZE-1]
        return hash_string

    @classmethod
    def get_settings(cls, user: str):
        if not user:
            return None
        return cls.query.filter(cls.user == cls._hash_user(user)).first()

