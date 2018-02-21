from .. import db
from . import STD_STRING_SIZE


class ItemType (db.Model):

    __tablename__ = 'ItemType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    name_schema = db.Column(db.String(STD_STRING_SIZE), unique=True)
    lendable = db.Column(db.Boolean, default=True)
    lending_duration = db.Column(db.Time, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE), nullable=True)
    how_to = db.Column(db.Text, nullable=True)

    def __init__(self, name: str, name_schema: str, visible_for: str='', how_to: str=''):
        self.name = name
        self.name_schema = name_schema

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for
        
        if how_to != '' and how_to != None:
            self.how_to = how_to


class ItemTypeToItemType (db.Model):

    __tablename__ = 'ItemTypeToItemType'

    parent_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'), primary_key=True)
    item_type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'), primary_key=True)

    def __init__(self, parent: ItemType, item_type: ItemType):
        self.parent = parent
        self.item_type = item_type
