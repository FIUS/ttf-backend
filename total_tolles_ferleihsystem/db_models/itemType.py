from .. import db
from . import STD_STRING_SIZE
from .attributeDefinition import AttributeDefinition


class ItemType (db.Model):

    __tablename__ = 'ItemType'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    name_schema = db.Column(db.String(STD_STRING_SIZE))
    lendable = db.Column(db.Boolean, default=True)
    lending_duration = db.Column(db.Integer, nullable=True)
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

    def update(self, name: str, name_schema: str, lendable: bool, lending_duration: int, visible_for: str, how_to:str):
        self.name = name
        self.name_schema = name_schema
        self.lendable = lendable
        self.lending_duration = lending_duration
        self.visible_for = visible_for
        self.how_to = how_to


class ItemTypeToItemType (db.Model):

    __tablename__ = 'ItemTypeToItemType'

    parent_id = db.Column(db.Integer, db.ForeignKey('ItemType.id', ondelete='CASCADE'), primary_key=True)
    item_type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'), primary_key=True)

    parent = db.relationship('ItemType', foreign_keys=[parent_id],
                             backref=db.backref('_contained_item_types', lazy='joined',
                                                single_parent=True, cascade="all, delete-orphan"))
    item_type = db.relationship('ItemType', foreign_keys=[item_type_id], lazy='joined')

    def __init__(self, parent_id: int, item_type_id: int):
        self.parent_id = parent_id
        self.item_type_id = item_type_id


class ItemTypeToAttributeDefinition (db.Model):

    __tablename__ = 'ItemTypeToAttributeDefinition'

    item_type_id = db.Column(db.Integer, db.ForeignKey('ItemType.id'), primary_key=True)
    attribute_definition_id = db.Column(db.Integer, db.ForeignKey('AttributeDefinition.id'), primary_key=True)

    item_type = db.relationship('ItemType', backref=db.backref('_item_type_to_attribute_definitions', lazy='joined'))
    attribute_definition = db.relationship('AttributeDefinition', lazy='joined')

    def __init__(self, item_type_id: int, attribute_definition_id: int):
        self.item_type_id = item_type_id
        self.attribute_definition_id = attribute_definition_id
