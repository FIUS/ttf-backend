"""
Module containing database models for everything concerning Item-Tags.
"""

from .. import DB
from . import STD_STRING_SIZE
from .attributeDefinition import AttributeDefinition

__all__ = [ 'Tag', 'TagToAttributeDefinition' ]

class Tag(DB.Model):
    """
    The representation of a Item-Tag
    """

    __tablename__ = 'Tag'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True)
    lending_duration = DB.Column(DB.Integer)
    deleted = DB.Column(DB.Boolean, default=False)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE))

    def __init__(self, name: str, lending_duration: int, visible_for: str):
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    def update(self, name: str, lending_duration: int, visible_for: str):
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for

class TagToAttributeDefinition (DB.Model):

    __tablename__ = 'TagToAttributeDefinition'

    tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'), primary_key=True)
    attribute_definition_id = DB.Column(DB.Integer, DB.ForeignKey('AttributeDefinition.id'), primary_key=True)

    tag = DB.relationship(Tag, backref=DB.backref('_tag_to_attribute_definitions', lazy='joined'))
    attribute_definition = DB.relationship('AttributeDefinition')

    def __init__(self, tag_id: int, attribute_definition_id: int):
        self.tag_id = tag_id
        self.attribute_definition_id = attribute_definition_id
