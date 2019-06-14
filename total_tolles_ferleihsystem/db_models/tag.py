"""
Module containing database models for everything concerning Item-Tags.
"""
import time

from .. import DB
from . import STD_STRING_SIZE
from . import attributeDefinition
from . import item

__all__ = [ 'Tag', 'TagToAttributeDefinition' ]

class Tag(DB.Model):
    """
    The representation of a Item-Tag
    """

    __tablename__ = 'Tag'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True)
    lending_duration = DB.Column(DB.Integer)
    deleted_time = DB.Column(DB.Integer, default=None)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE))

    def __init__(self, name: str, lending_duration: int, visible_for: str):
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    def update(self, name: str, lending_duration: int, visible_for: str):
        self.name = name
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    @property
    def deleted(self):
        return self.deleted_time is not None

    @deleted.setter
    def deleted(self, value: bool):
        if value:
            self.deleted_time = int(time.time())
        else:
            self.deleted_time = None

    def unassociate_attr_def(self, attribute_definition_id):
        """
        Does all necessary changes to the database for unassociating a attribute definition from this tag.
        Does not commit the changes.
        """
        if attributeDefinition.AttributeDefinition.query.filter(attributeDefinition.AttributeDefinition.id == attribute_definition_id).filter(attributeDefinition.AttributeDefinition.deleted_time == None).first() is None:
            return(400, 'Requested attribute definition not found!', False)
        association = (TagToAttributeDefinition
                       .query
                       .filter(TagToAttributeDefinition.tag_id == self.id)
                       .filter(TagToAttributeDefinition.attribute_definition_id == attribute_definition_id)
                       .first())
        if association is None:
            return(204, '', False)

        itads = item.ItemToAttributeDefinition.query.filter(item.ItemToAttributeDefinition.attribute_definition_id == attribute_definition_id).all()

        items = [itad.item for itad in itads]

        DB.session.delete(association)

        for i in items:
            _, attributes_to_delete, _ = i.get_attribute_changes([attribute_definition_id], True)
            for attr in attributes_to_delete:
                attr.deleted = True
        return(204, '', True)


class TagToAttributeDefinition (DB.Model):

    __tablename__ = 'TagToAttributeDefinition'

    tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'), primary_key=True)
    attribute_definition_id = DB.Column(DB.Integer, DB.ForeignKey('AttributeDefinition.id'), primary_key=True)

    tag = DB.relationship(Tag, lazy='select', backref=DB.backref('_tag_to_attribute_definitions', lazy='select'))
    attribute_definition = DB.relationship('AttributeDefinition', lazy='joined')

    def __init__(self, tag_id: int, attribute_definition_id: int):
        self.tag_id = tag_id
        self.attribute_definition_id = attribute_definition_id
