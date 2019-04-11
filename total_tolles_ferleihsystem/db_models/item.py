"""
The database models of the item and all connected tables
"""
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint
import string
from json import loads
from datetime import date
import time

from .. import DB, LENDING_LOGGER
from . import STD_STRING_SIZE

from . import itemType
from .tag import TagToAttributeDefinition

__all__ = [
    'Item',
    'File',
    'Lending',
    'ItemToItem',
    'ItemToTag',
    'ItemToAttributeDefinition'
]


class Item(DB.Model):
    """
    This data model represents a single lendable item
    """
    __tablename__ = 'Item'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE))
    update_name_from_schema = DB.Column(DB.Boolean, default=True, nullable=False)
    type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'))
    lending_id = DB.Column(DB.Integer, DB.ForeignKey('Lending.id'), default=None, nullable=True)
    lending_duration = DB.Column(DB.Integer, nullable=True)  # in seconds
    due = DB.Column(DB.Integer, default=-1) # unix time
    deleted = DB.Column(DB.Boolean, default=False)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)

    type = DB.relationship('ItemType', lazy='joined')
    lending = DB.relationship('Lending', lazy='select', 
                              backref=DB.backref('_items', lazy='select'))

    __table_args__ = (
        UniqueConstraint('name', 'type_id', name='_name_type_id_uc'),
    )

    def __init__(self, update_name_from_schema: bool, name: str, type_id: int, lending_duration: int = -1,
                 visible_for: str = ''):
        self.update_name_from_schema = update_name_from_schema

        self.name = name

        self.type_id = type_id

        if lending_duration >= 0:
            self.lending_duration = lending_duration

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for

    def update(self, update_name_from_schema: bool, name: str, type_id: int, lending_duration: int = -1,
               visible_for: str = ''):
        """
        Function to update the objects data
        """
        self.update_name_from_schema = update_name_from_schema

        if self.update_name_from_schema:
            self.name = self.name_schema_name
        else:
            self.name = name

        self.type_id = type_id
        self.lending_duration = lending_duration
        self.visible_for = visible_for

    @property
    def is_currently_lent(self):
        """
        If the item is currently lent.
        """
        return self.lending is not None

    @property
    def parent(self):
        if self._parents:
            return self._parents[0].parent
        return None

    @property
    def effective_lending_duration(self):
        """
        The effective lending duration computed from item type, tags and item
        """
        if self.lending_duration and (self.lending_duration >= 0):
            return self.lending_duration

        tag_lending_duration = min((t.tag.lending_duration for t in self._tags if t.tag.lending_duration > 0), default=-1)

        if tag_lending_duration >= 0:
            return tag_lending_duration

        return self.type.lending_duration

    @property
    def name_schema_name(self):
        template = string.Template(self.type.name_schema)
        attributes = {}
        for attr in self._attributes:
            if attr.value:
                try:
                    attributes[attr.attribute_definition.name] = loads(attr.value)
                except:
                    pass
            else:
                attr_def = loads(attr.attribute_definition.jsonschema)
                attributes[attr.attribute_definition.name] = attr_def.get('default', '')

        parent = "".join(item.parent.name for item in ItemToItem.query.filter(ItemToItem.item_id == self.id).all())

        today = date.today()
        times = {
            'c_year': today.year,
            'c_month': today.month,
            'c_day': today.day,
            'c_date': today.strftime('%d.%b.%Y'),
            'c_date_iso': today.isoformat(),
        }
        return template.safe_substitute(attributes, type=self.type.name, parent=parent, **times)

    def delete(self):
        if self.is_currently_lent:
            return(400, "Requested item is currently lent!", False)
        self.deleted = True

        for element in self._attributes:
            element.delete()

    # Not intended -neumantm
    #    for element in self._contained_items:
    #        DB.session.delete(element)
    #    for element in self._tags:
    #        DB.session.delete(element)
        return(204, "", True)

    def get_attribute_changes(self, definition_ids, remove: bool = False):
        """
        Get a list of attributes to add, to delete and to undelete,
        considering all definition_ids in the list and whether to add or remove them.
        """
        attributes_to_add = []
        attributes_to_delete = []
        attributes_to_undelete = []
        for def_id in definition_ids:
            itads = self._attributes
            exists = False
            for itad in itads:
                if(itad.attribute_definition_id == def_id):
                    exists = True
                    if(remove):
                        # Check if multiple sources bring it, if yes don't delete it.
                        sources = 0
                        if(def_id in [ittad.attribute_definition_id for ittad in self.type._item_type_to_attribute_definitions if not ittad.attribute_definition.deleted]):
                            sources += 1
                        for tag in [itt.tag for itt in self._tags]:
                            if(def_id in [ttad.attribute_definition_id for ttad in tag._tag_to_attribute_definitions if not ttad.attribute_definition.deleted]):
                                sources += 1
                        if sources == 1:
                            attributes_to_delete.append(itad)
                    elif(itad.deleted):
                        attributes_to_undelete.append(itad)

            if not exists and not remove:
                attributes_to_add.append(ItemToAttributeDefinition(self.id,
                                                                   def_id,
                                                                   ""))  # TODO: Get default if possible.
        return attributes_to_add, attributes_to_delete, attributes_to_undelete

    def get_new_attributes_from_type(self, type_id: int):
        """
        Get a list of attributes to add to a new item which has the given type.
        """

        item_type_attribute_definitions = (itemType.ItemTypeToAttributeDefinition
                                           .query
                                           .filter(itemType.ItemTypeToAttributeDefinition.item_type_id == type_id)
                                           .all())
        attributes_to_add, _, _ = self.get_attribute_changes(
            [ittad.attribute_definition_id for ittad in item_type_attribute_definitions if not ittad.item_type.deleted], False)

        return attributes_to_add

    def get_attribute_changes_from_type_change(self, from_type_id: int, to_type_id: int):
        """
        Get a list of attributes to add, to delete and to undelete,
        when this item would now switch from the first to the second type.
        """
        old_item_type_attr_defs = (itemType.ItemTypeToAttributeDefinition
                                   .query
                                   .filter(itemType.ItemTypeToAttributeDefinition.item_type_id == from_type_id)
                                   .all())

        new_item_type_attr_defs = (itemType.ItemTypeToAttributeDefinition
                                   .query
                                   .filter(itemType.ItemTypeToAttributeDefinition.item_type_id == to_type_id)
                                   .all())

        old_attr_def_ids = [ittad.attribute_definition_id for ittad in old_item_type_attr_defs]
        new_attr_def_ids = [ittad.attribute_definition_id for ittad in new_item_type_attr_defs]

        added_attr_def_ids = [attr_def_id for attr_def_id in new_attr_def_ids if attr_def_id not in old_attr_def_ids]
        removed_attr_def_ids = [attr_def_id for attr_def_id in old_attr_def_ids if attr_def_id not in new_attr_def_ids]

        attributes_to_add, _, attributes_to_undelete = self.get_attribute_changes(added_attr_def_ids, False)
        _, attributes_to_delete, _ = self.get_attribute_changes(removed_attr_def_ids, True)

        return attributes_to_add, attributes_to_delete, attributes_to_undelete

    def get_attribute_changes_from_tag(self, tag_id: int, remove: bool = False):
        """
        Get a list of attributes to add, to delete and to undelete,
        when this item would now get that tag or loose that tag.
        """

        tag_attribute_definitions = (TagToAttributeDefinition
                                     .query
                                     .filter(TagToAttributeDefinition.tag_id == tag_id)
                                     .all())
        return self.get_attribute_changes([ttad.attribute_definition_id for ttad in tag_attribute_definitions], remove)


class File(DB.Model):
    """
    This data model represents a file attached to a item
    """

    __tablename__ = 'File'

    id = DB.Column(DB.Integer, primary_key=True)
    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), nullable=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)
    file_type = DB.Column(DB.String(STD_STRING_SIZE))
    file_hash = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)
    creation = DB.Column(DB.DateTime, server_default=func.now())
    invalidation = DB.Column(DB.DateTime, nullable=True)
    visible_for = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)

    item = DB.relationship('Item', lazy='select', backref=DB.backref('_files', lazy='select',
                                                                     single_parent=True,
                                                                     cascade="all, delete-orphan"))

    def __init__(self, name: str, file_type: str, file_hash: str, item_id: int = None, visible_for: str = ''):
        if item_id is not None:
            self.item_id = item_id
        self.name = name
        self.file_type = file_type
        self.file_hash = file_hash

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for

    def update(self, name: str, file_type: str, invalidation, item_id: int, visible_for: str = '') -> None:
        """
        Function to update the objects data
        """
        self.name = name
        self.file_type = file_type
        self.invalidation = invalidation
        self.item_id = item_id
        self.visible_for = visible_for


class Lending(DB.Model):
    """
    This data model represents a Lending
    """
    __tablename__ = 'Lending'

    id = DB.Column(DB.Integer, primary_key=True)
    moderator = DB.Column(DB.String(STD_STRING_SIZE))
    user = DB.Column(DB.String(STD_STRING_SIZE))
    date = DB.Column(DB.Integer) #unix time
    deposit = DB.Column(DB.String(STD_STRING_SIZE))

    def __repr__(self):
        ret = "Lending by "
        ret += self.moderator
        ret += " to "
        ret += self.user
        ret += " at "
        ret += str(self.date)
        ret += " with "
        ret += self.deposit
        ret += ". Items:"
        ret += str([str(item.id) for item in self._items])
        return ret

    def __init__(self, moderator: str, user: str, deposit: str, item_ids: list):
        self.moderator = moderator
        self.user = user
        self.date = int(time.time())
        self.deposit = deposit
        for element in item_ids:
            item = Item.query.filter(Item.id == element).filter(Item.deleted == False).first()
            if item is None:
                raise ValueError("Item not found:" + str(element))
            if not item.type.lendable:
                raise ValueError("Item not lendable:" + str(element))
            if item.is_currently_lent:
               raise ValueError("Item already lent:" + str(element))
            item.lending = self
            item.due = self.date + item.effective_lending_duration
        LENDING_LOGGER.info("New lending: %s", repr(self))
        

    def update(self, moderator: str, user: str, deposit: str, item_ids: list):
        """
        Function to update the objects data
        """
        self.moderator = moderator
        self.user = user
        self.deposit = deposit
        old_items = self._items
        new_items = []

        for element in item_ids:
            item = Item.query.filter(Item.id == element).filter(Item.deleted == False).first()
            if item is None:
                raise ValueError("Item not found:" + str(element))
            new_items.append(item)
        
        items_to_remove = [item for item in old_items if item not in new_items]
        items_to_add = [item for item in new_items if item not in old_items]

        for item in items_to_remove:
            item.lending = None
            item.due = -1
        
        for item in items_to_add:
            if not item.type.lendable:
                raise ValueError("Item not lendable:" + str(item))
            if item.is_currently_lent:
                raise ValueError("Item already lent:" + str(item))
            item.lending = self
            item.due = self.date + item.effective_lending_duration
        LENDING_LOGGER.info("Updated lending: %s", repr(self))


    def remove_items(self, item_ids: list):
        """
        Function to remove a list of items from this lending
        """
        for element in item_ids:
            item = Item.query.filter(Item.id == element).first()
            if item is None:
                raise ValueError("Item not found:" + str(element))
            item.lending = None
            item.due = -1
        LENDING_LOGGER.info("Updated lending(remove items): %s", repr(self))

    def pre_delete(self):
        LENDING_LOGGER.info("Deleting lending: %s", repr(self))
        for item in list(self._items):
            item.lending = None
            item.due = -1

class ItemToItem(DB.Model):

    __tablename__ = 'ItemToItem'

    parent_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)

    parent = DB.relationship('Item', foreign_keys=[parent_id], lazy='select',
                             backref=DB.backref('_contained_items', lazy='select',
                                                single_parent=True, cascade="all, delete-orphan"))
    item = DB.relationship('Item', foreign_keys=[item_id], lazy='select',
                           backref=DB.backref('_parents', lazy='select',
                                              single_parent=True, cascade="all, delete-orphan"))

    def __init__(self, parent_id: int, item_id: int):
        self.parent_id = parent_id
        self.item_id = item_id


class ItemToTag (DB.Model):

    __tablename__ = 'ItemToTag'

    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'), primary_key=True)

    item = DB.relationship('Item', lazy='select', backref=DB.backref('_tags', lazy='select',
                                                                     single_parent=True, cascade="all, delete-orphan"))
    tag = DB.relationship('Tag', lazy='joined')

    def __init__(self, item_id: int, tag_id: int):
        self.item_id = item_id
        self.tag_id = tag_id


class ItemToAttributeDefinition (DB.Model):

    __tablename__ = 'ItemToAttributeDefinition'

    item_id = DB.Column(DB.Integer, DB.ForeignKey('Item.id'), primary_key=True)
    attribute_definition_id = DB.Column(DB.Integer, DB.ForeignKey('AttributeDefinition.id'), primary_key=True)
    value = DB.Column(DB.String(STD_STRING_SIZE))
    deleted = DB.Column(DB.Boolean, default=False)

    item = DB.relationship('Item', lazy='select', backref=DB.backref('_attributes', lazy='select',
                                                                     single_parent=True, cascade="all, delete-orphan"))
    attribute_definition = DB.relationship('AttributeDefinition', lazy='select',
                                           backref=DB.backref('_item_to_attribute_definitions', lazy='select'))

    def __init__(self, item_id: int, attribute_definition_id: int, value: str):
        self.item_id = item_id
        self.attribute_definition_id = attribute_definition_id
        self.value = value

    def update(self, value: str) -> None:
        """
        Update the value
        """
        self.value = value

        if self.item.update_name_from_schema:
            self.item.name = self.item.name_schema_name

    def delete(self) -> None:
        """
        Soft-deletes this association
        """
        self.deleted = True

    def undelete(self) -> None:
        """
        Undeletes this association
        """
        self.deleted = False

    @property
    def is_deleted(self) -> bool:
        """
        Checks whether this association is currently soft deleted
        """
        return self.deleted
