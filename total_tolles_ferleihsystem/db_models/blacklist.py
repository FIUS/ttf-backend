from .. import db
from . import STD_STRING_SIZE


class Blacklist (db.Model):

    __tablename__ = 'Blacklist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True, index=True)
    system_wide = db.Column(db.Boolean, default=False)
    reason = db.Column(db.Text, nullable=True)

    #TODO add relationship for user

    def __init__(self, name: str, system_wide: bool = False, reason: str = None):
        self.name = name

        if system_wide:
            self.system_wide = True
            self.reason = reason


class BlacklistToItemType (db.Model):

    __tablename__ = 'BlacklistToItemType'

    user_id = db.Column(db.Integer, db.ForeignKey('Blacklist.id'), primary_key=True)
    #TODO itemType_id = db.Column()

    def __init__(self, user: Blacklist):
        #TODO itemType: ItemType
        self.user = user
