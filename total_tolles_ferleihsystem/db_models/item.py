import datetime

from .. import db
from . import STD_STRING_SIZE
from .itemType import ItemType, ItemTypeToAttributeDefinition
from .tag import Tag, TagToAttributeDefinition
from .attributeDefinition import AttributeDefinition

class Item (db.Model):

    __tablename__ = 'Item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'))
    lending_duration = db.Column(db.Integer) #TODO add default value
    deleted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE), nullable=True)

    type = db.relationship('ItemType', lazy='joined')

    def __init__(self, name: str, type_id: int, lending_duration: int=0, visible_for: str=''):
        self.name = name
        self.type_id = type_id

        if lending_duration != 0:
           self.lending_duration = lending_duration
           #TODO fix time handling/conversion what ever

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for

    def update(self, name: str, type_id: int, lending_duration: int=0, visible_for: str=''):
        self.name = name
        self.type_id = type_id
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    @property
    def lending_id(self):
        """
        The lending_id this item is currently associated with. -1 if not lended. 
        """
        lending_to_item = ItemToLending.query.filter(ItemToLending.item_id == self.id).first()
        if lending_to_item is None:
            return -1
        return lending_to_item.lending_id

    @property
    def is_currently_lended(self):
        """
        If the item is currently lended.
        """
        return self.lending_id != -1

    def get_lending_duration(self):
        return self.lending_duration

class File (db.Model):

    __tablename__ = 'File'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'))
    name = db.Column(db.String(STD_STRING_SIZE))
    path = db.Column(db.String(STD_STRING_SIZE))

    item = db.relationship('Item', lazy='joined', backref=db.backref('_files', lazy='joined',
                                                                     single_parent=True,
                                                                     cascade="all, delete-orphan"))

    def __init__(self, item: Item, name: str, path: str):
        self.item = item
        self.name = name
        self.path = path


class Lending (db.Model):

    __tablename__ = 'Lending'

    id = db.Column(db.Integer, primary_key=True)
    # FIXME used to have Integer as type possibly missing table ?
    moderator = db.Column(db.String(STD_STRING_SIZE))
    user = db.Column(db.String(STD_STRING_SIZE))
    date = db.Column(db.DateTime)
    deposit = db.Column(db.String(STD_STRING_SIZE))

    def __init__(self, moderator: str, user: str, deposit: str):
        self.moderator = moderator
        self.user = user
        self.date = datetime.datetime.now()
        self.deposit = deposit

    def update(self, moderator: str, user: str, deposit: str):
        self.moderator = moderator
        self.user = user
        self.deposit = deposit


class ItemToItem (db.Model):

    __tablename__ = 'ItemToItem'

    parent_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)

    parent = db.relationship('Item', foreign_keys=[parent_id],
                             backref=db.backref('_contained_items', lazy='joined',
                                                single_parent=True, cascade="all, delete-orphan"))
    item = db.relationship('Item', foreign_keys=[item_id], lazy='joined')

    def __init__(self, parent_id: int, item_id: int):
        self.parent_id = parent_id
        self.item_id = item_id


class ItemToLending (db.Model):

    __tablename__ = 'ItemToLending'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    lending_id = db.Column(db.Integer, db.ForeignKey('Lending.id'), primary_key=True)
    due = db.Column(db.DateTime)

    item = db.relationship('Item', backref=db.backref('_lending', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    lending = db.relationship('Lending', backref=db.backref('itemLendings', lazy='joined',
                                                            single_parent=True,
                                                            cascade="all, delete-orphan"), lazy='joined')

    def __init__(self, item: Item, lending: Lending):
        self.item = item
        self.lending = lending
        self.due = lending.date + datetime.timedelta(0,item.get_lending_duration())


class ItemToTag (db.Model):

    __tablename__ = 'ItemToTag'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('Tag.id'), primary_key=True)

    item = db.relationship('Item', backref=db.backref('_tags', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    tag = db.relationship('Tag', lazy='joined')

    def __init__(self, item_id: int, tag_id: int):
        self.item_id = item_id
        self.tag_id = tag_id


class ItemAttribute (db.Model):

    __tablename__ = 'ItemAttributes'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    attribute_definition_id = db.Column(db.Integer, db.ForeignKey('AttributeDefinition.id'), primary_key=True)
    value = db.Column(db.String(STD_STRING_SIZE))

    item = db.relationship('Item', backref=db.backref('_attributes', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    attribute_definition = db.relationship('AttributeDefinition', lazy='joined')

    def __init__(self, item_id: int, attribute_definition_id: int, value: str):
        self.item_id = item_id
        self.attribute_definition_id = attribute_definition_id
        self.value = value