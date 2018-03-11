from .. import db
from . import STD_STRING_SIZE
from .itemType import ItemType
from .tag import Tag
from .attribute import Attribute


class Item (db.Model):

    __tablename__ = 'Item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'))
    lending_duration = db.Column(db.Time) #TODO add default value
    delted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE), nullable=True)

    type = db.relationship('ItemType', lazy='joined')

    def __init__(self, name: str, type: ItemType, lending_duration: int=0, visible_for: str=''):
        self.name = name
        self.type = type

        if lending_duration != 0:
           self.lending_duration = lending_duration
           #TODO fix time handling/conversion what ever

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for


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

    def __init__(self, moderator: str, user: str, date: any, deposit: str):
        # TODO Fabi fix date !
        self.moderator = moderator
        self.user = user
        self.date = date
        self.deposit = deposit


class ItemToItem (db.Model):

    __tablename__ = 'ItemToItem'

    parent_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)

    parent = db.relationship('Item', foreign_keys=[parent_id],
                             backref=db.backref('_contained_items', lazy='joined',
                                                single_parent=True, cascade="all, delete-orphan"))
    item = db.relationship('Item', foreign_keys=[item_id], lazy='joined')

    def __init__(self, parent: Item, item: Item):
        self.parent = parent
        self.item = item


class ItemToLending (db.Model):

    __tablename__ = 'ItemToLending'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    lending_id = db.Column(db.Integer, db.ForeignKey('Lending.id'), primary_key=True)
    due = db.Column(db.DateTime)

    item = db.relationship('Item', backref=db.backref('_lending', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    lending = db.relationship('Lending', backref=db.backref('_items', lazy='joined',
                                                            single_parent=True,
                                                            cascade="all, delete-orphan"), lazy='joined')

    def __init__(self, item: Item, lending: Lending, due: any):
        # TODO Fabi fix date
        self.item = item
        self.lending = lending
        self.due = due


class ItemToTag (db.Model):

    __tablename__ = 'ItemToTag'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('Tag.id'), primary_key=True)

    item = db.relationship('Item', backref=db.backref('_tags', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    tag = db.relationship('Tag', lazy='joined')

    def __init__(self, item: Item, tag: Tag):
        self.item = item
        self.tag = tag


class ItemToAttribute (db.Model):

    __tablename__ = 'ItemToAttribute'

    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('Attribute.id'), primary_key=True)

    item = db.relationship('Item', backref=db.backref('_attributes', lazy='joined',
                                                      single_parent=True, cascade="all, delete-orphan"))
    attribute = db.relationship('Attribute', lazy='joined')

    def __init__(self, item: Item, attribute: Attribute):
        self.item = item
        self.attribute = attribute