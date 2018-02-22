from .. import db
from . import STD_STRING_SIZE
from .itemType import ItemType


class Blacklist (db.Model):

    __tablename__ = 'Blacklist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True, index=True)
    system_wide = db.Column(db.Boolean, default=False)
    reason = db.Column(db.Text, nullable=True)

    def __init__(self, name: str, system_wide: bool = False, reason: str = None):
        self.name = name

        if system_wide:
            self.system_wide = True
            self.reason = reason


class BlacklistToItemType (db.Model):

    __tablename__ = 'BlacklistToItemType'

    user_id = db.Column(db.Integer, db.ForeignKey('Blacklist.id'), primary_key=True)
    item_type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'), primary_key=True)
    end_time = db.Column(db.DateTime, nullable=True)
    reason = db.Column(db.Text, nullable=True)

    def __init__(self, user: Blacklist, item_type: ItemType, end_time: any=None, reason: str=None):
        #TODO Fabi pls FIX duration time
        self.user = user
        self.item_type = item_type

        if self.end_time != None:
            self.end_time = end_time
            self.reason = reason
