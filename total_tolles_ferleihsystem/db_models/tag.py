from .. import db
from . import STD_STRING_SIZE
from .attribute import AttributeDefinition


class Tag (db.Model):

    __tablename__ = 'Tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE))
    lending_duration = db.Column(db.Time)
    deleted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE))

    def __init__(self, name: str, lending_duration: any, visible_for: str):
        #TODO Fabi fix date/time formats everywhere
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for


class TagToAttributeDefinition (db.Model):

    __tablename__ = 'TagToAttributeDefinition'

    tag_id = db.Column(db.Integer, db.ForeignKey('Tag.id'), primary_key=True)
    attribute_definition_id = db.Column(db.Integer, db.ForeignKey('AttributeDefinition.id'), primary_key=True)
    lending_duration = db.Column(db.Time)

    tag = db.relationship(Tag, backref=db.backref('_tag_to_attribute_definitions', lazy='joined'))
    attribute_definition = db.relationship('AttributeDefinition')

    def __init__(self, tag: Tag, attribute_definition: AttributeDefinition, lending_duration: any):
        #TODO Fabi plz fix date/time
        self.tag = tag
        self.attribute_definition = attribute_definition
        self.lending_duration = lending_duration
