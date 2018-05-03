from .. import DB
from . import STD_STRING_SIZE
from .item import AttributeDefinition


class ItemType (DB.Model):

    __tablename__ = 'ItemType'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True)
    name_schema = DB.Column(DB.String(STD_STRING_SIZE))
    lendable = DB.Column(DB.Boolean, default=True)
    lending_duration = DB.Column(DB.Integer, nullable=True)
    deleted = DB.Column(DB.Boolean, default=False)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)
    how_to = DB.Column(DB.Text, nullable=True)

    def __init__(self, name: str, name_schema: str, visible_for: str = '', how_to: str = ''):
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


class ItemTypeToItemType (DB.Model):

    __tablename__ = 'ItemTypeToItemType'

    parent_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id', ondelete='CASCADE'), primary_key=True)
    item_type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'), primary_key=True)

    parent = DB.relationship('ItemType', foreign_keys=[parent_id],
                             backref=DB.backref('_contained_item_types', lazy='joined',
                                                single_parent=True, cascade="all, delete-orphan"))
    item_type = DB.relationship('ItemType', foreign_keys=[item_type_id], lazy='joined')

    def __init__(self, parent_id: int, item_type_id: int):
        self.parent_id = parent_id
        self.item_type_id = item_type_id


class ItemTypeToAttributeDefinition (DB.Model):

    __tablename__ = 'ItemTypeToAttributeDefinition'

    item_type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'), primary_key=True)
    attribute_definition_id = DB.Column(DB.Integer, DB.ForeignKey('AttributeDefinition.id'), primary_key=True)

    item_type = DB.relationship('ItemType', backref=DB.backref('_item_type_to_attribute_definitions', lazy='joined'))
    attribute_definition = DB.relationship('AttributeDefinition', lazy='joined')

    def __init__(self, item_type_id: int, attribute_definition_id: int):
        self.item_type_id = item_type_id
        self.attribute_definition_id = attribute_definition_id
