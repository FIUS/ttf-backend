from .. import DB
from . import STD_STRING_SIZE
from .itemType import ItemType


__all__=['Blacklist', 'BlacklistToItemType']

class Blacklist (DB.Model):

    __tablename__ = 'Blacklist'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True, index=True)
    system_wide = DB.Column(DB.Boolean, default=False)
    reason = DB.Column(DB.Text, nullable=True)

    def __init__(self, name: str, system_wide: bool = False, reason: str = None):
        self.name = name

        if system_wide:
            self.system_wide = True
            self.reason = reason


class BlacklistToItemType (DB.Model):

    __tablename__ = 'BlacklistToItemType'

    user_id = DB.Column(DB.Integer, DB.ForeignKey('Blacklist.id'), primary_key=True)
    item_type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'), primary_key=True)
    end_time = DB.Column(DB.Integer, nullable=True)
    reason = DB.Column(DB.Text, nullable=True)

    user = DB.relationship('Blacklist', lazy='select', backref=DB.backref('_item_types', lazy='select',
                                                           single_parent=True, cascade="all, delete-orphan"))
    item_type = DB.relationship('ItemType', lazy='joined')

    def __init__(self, user: Blacklist, item_type: ItemType, end_time: int=None, reason: str=None):
        self.user = user
        self.item_type = item_type
        self.reason = reason
        self.end_time = end_time
