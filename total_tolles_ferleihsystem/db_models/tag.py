"""
Module containing database models for everything concerning Item-Tags.
"""

from .. import db
from . import STD_STRING_SIZE
from .attribute import AttributeDefinition

class Tag(db.Model):
    """
    The representation of a Item-Tag
    """

    __tablename__ = 'Tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    lending_duration = db.Column(db.Integer)
    deleted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE))

    def __init__(self, name: str, lending_duration: int, visible_for: str):
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for


class TagToAttributeDefinition (db.Model):

    __tablename__ = 'TagToAttributeDefinition'

    tag_id = db.Column(db.Integer, db.ForeignKey('Tag.id'), primary_key=True)
    attribute_definition_id = db.Column(db.Integer, db.ForeignKey('AttributeDefinition.id'), primary_key=True)
    lending_duration = db.Column(db.Integer)

    tag = db.relationship(Tag, backref=db.backref('_tag_to_attribute_definitions', lazy='joined'))
    attribute_definition = db.relationship('AttributeDefinition')

    def __init__(self, tag: Tag, attribute_definition: AttributeDefinition, lending_duration: int):
        self.tag = tag
        self.attribute_definition = attribute_definition
        self.lending_duration = lending_duration
