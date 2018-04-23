"""
The database models of the item and all connected tables
"""

import datetime

from .. import DB
from . import STD_STRING_SIZE

class Item(DB.Model):
    """
    This data model represents a single lendable item
    """
    __tablename__ = 'Item'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True)
    type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'))
    lending_duration = DB.Column(DB.Integer) #TODO add default value
    deleted = DB.Column(DB.Boolean, default=False)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)

    type = DB.relationship('ItemType', lazy='joined')

    def __init__(self, name: str, type_id: int, lending_duration: int = 0, visible_for: str = ''):
        self.name = name
        self.type_id = type_id

        if lending_duration != 0:
            self.lending_duration = lending_duration
            #TODO fix time handling/conversion what ever

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for

    def update(self, name: str, type_id: int, lending_duration: int = 0, visible_for: str = ''):
        """
        Function to update the objects data
        """
        self.name = name
        self.type_id = type_id
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    @property
    def lending_id(self):
        """
        The lending_id this item is currently associated with. -1 if not lent.
        """
        lending_to_item = ItemToLending.query.filter(ItemToLending.item_id == self.id).first()
        if lending_to_item is None:
            return -1
        return lending_to_item.lending_id

    @property
    def is_currently_lent(self):
        """
        If the item is currently lent.
        """
        return self.lending_id != -1

    def get_lending_duration(self):
        return self.lending_duration

class File(DB.Model):
    """
    This data model represents a file attached to a item
    """
    __tablename__ = 'File'

    id = DB.Column(DB.Integer, primary_key=True)
    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'))
    name = DB.Column(DB.String(STD_STRING_SIZE))
    path = DB.Column(DB.String(STD_STRING_SIZE))

    item = DB.relationship('Item', lazy='joined', backref=DB.backref('_files', lazy='joined',
                                                                     single_parent=True,
                                                                     cascade="all, delete-orphan"))

    def __init__(self, item: Item, name: str, path: str):
        self.item = item
        self.name = name
        self.path = path


class Lending(DB.Model):
    """
    This data model represents a Lending
    """
    __tablename__ = 'Lending'

    id = DB.Column(DB.Integer, primary_key=True)
    #FIXME used to have Integer as type possibly missing table ?
    moderator = DB.Column(DB.String(STD_STRING_SIZE))
    user = DB.Column(DB.String(STD_STRING_SIZE))
    date = DB.Column(DB.DateTime)
    deposit = DB.Column(DB.String(STD_STRING_SIZE))

    def __init__(self, moderator: str, user: str, deposit: str):
        self.moderator = moderator
        self.user = user
        self.date = datetime.datetime.now()
        self.deposit = deposit

    def update(self, moderator: str, user: str, deposit: str):
        """
        Function to update the objects data
        """
        self.moderator = moderator
        self.user = user
        self.deposit = deposit


class ItemToItem (DB.Model):

    __tablename__ = 'ItemToItem'

    parent_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)

    parent = DB.relationship('Item', foreign_keys=[parent_id],
                             backref=DB.backref('_contained_items', lazy='joined',
                                                single_parent=True, cascade="all, delete-orphan"))
    item = DB.relationship('Item', foreign_keys=[item_id], lazy='joined')

    def __init__(self, parent_id: int, item_id: int):
        self.parent_id = parent_id
        self.item_id = item_id


class ItemToLending (DB.Model):

    __tablename__ = 'ItemToLending'

    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    lending_id = DB.Column(DB.Integer, DB.ForeignKey('Lending.id'), primary_key=True)
    due = DB.Column(DB.DateTime)

    item = DB.relationship('Item', backref=DB.backref('_lending', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    lending = DB.relationship('Lending', backref=DB.backref('itemLendings', lazy='joined',
                                                            single_parent=True,
                                                            cascade="all, delete-orphan"), lazy='joined')

    def __init__(self, item: Item, lending: Lending):
        self.item = item
        self.lending = lending
        self.due = lending.date + datetime.timedelta(0, item.get_lending_duration())


class ItemToTag (DB.Model):

    __tablename__ = 'ItemToTag'

    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'), primary_key=True)

    item = DB.relationship('Item', backref=DB.backref('_tags', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    tag = DB.relationship('Tag', lazy='joined')

    def __init__(self, item_id: int, tag_id: int):
        self.item_id = item_id
        self.tag_id = tag_id


class ItemAttribute (DB.Model):

    __tablename__ = 'ItemAttributes'

    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    attribute_definition_id = DB.Column(DB.Integer, DB.ForeignKey('AttributeDefinition.id'), primary_key=True)
    value = DB.Column(DB.String(STD_STRING_SIZE))

    item = DB.relationship('Item', backref=DB.backref('_attributes', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    attribute_definition = DB.relationship('AttributeDefinition', lazy='joined')

    def __init__(self, item_id: int, attribute_definition_id: int, value: str):
        self.item_id = item_id
        self.attribute_definition_id = attribute_definition_id
        self.value = value
