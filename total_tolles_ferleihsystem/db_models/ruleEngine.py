"""
The database models of the rule engine tables
"""
from sqlalchemy.schema import UniqueConstraint
from .. import DB
from . import STD_STRING_SIZE
from . import itemType
from . import tag

__all__ = [
    'Rule',
    'KeyValueStore',
    'SubRule',
    'SubRuleToTag'
]


class Rule(DB.Model):
    """
    This represents a block of subrules and mostly consists of metadata
    """
    __tablename__ = 'Rule'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STD_STRING_SIZE), unique=True)
    description = DB.Column(DB.Text, nullable=True)
    last_run = DB.Column(DB.Integer, nullable=True) # seconds since epoch
    next_run = DB.Column(DB.Integer, nullable=True) # seconds since epoch
    execution_schedule = DB.Column(DB.Text, nullable=True)

    def __init__(self, name: str, description: str, execution_schedule: str):
        self.name = name
        self.description = description
        self.execution_schedule = execution_schedule


class KeyValueStore(DB.Model):
    """
    This represents a simple key value store used by the rule engine
    """
    __tablename__ = 'KeyValueStore'

    key = DB.Column(DB.String(STD_STRING_SIZE), primary_key=True)
    value = DB.Column(DB.String(STD_STRING_SIZE), nullable=True)

    def __init__(self, key: str, value: str):
        self.key = key
        if value != '' and value != None:
            self.value = value


class SubRule(DB.Model):
    """
    This represents one single minimal instruction in a rule
    """
    __tablename__ = 'SubRule'

    id = DB.Column(DB.Integer, primary_key=True)
    rule_id = DB.Column(DB.Integer, DB.ForeignKey('Rule.id'))
    position = DB.Column(DB.Integer, default=-1)
    variable_key = DB.Column(DB.String(STD_STRING_SIZE), DB.ForeignKey('KeyValueStore.key'))
    operator = DB.Column(DB.String(2))
    comparison = DB.Column(DB.String(STD_STRING_SIZE))
    type_id = DB.Column(DB.Integer, DB.ForeignKey('ItemType.id'))
    add_tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'))
    remove_tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'))

    rule = DB.relationship('Rule', lazy='select', backref=DB.backref('sub_rules', lazy='joined'))
    variable = DB.relationship('KeyValueStore', lazy='joined')
    type = DB.relationship('ItemType', lazy='select')
    add_tag = DB.relationship('Tag', foreign_keys=[add_tag_id], lazy='select')
    remove_tag = DB.relationship('Tag', foreign_keys=[remove_tag_id], lazy='select')

    __table_args__ = (
        UniqueConstraint('rule_id', 'position', name='_rule_id_position_uc'),
    )

    def __init__(self, rule_id: int, position: int, variable_key: str,
            operator: str, comparison: str, type_id: int, add_tag_id: int,
            remove_tag_id: int):
        self.rule_id = rule_id
        self.position = position
        self.variable_key = variable_key
        self.operator = operator
        self.comparison = comparison

        if type_id != 0 and type_id != None:
            self.type_id = type_id

        if add_tag_id != 0 and add_tag_id != None:
            self.add_tag_id = add_tag_id

        if remove_tag_id != 0 and remove_tag_id != None:
            self.remove_tag_id = remove_tag_id


class SubRuleToTag(DB.Model):
    """
    NxM connection table for subrules and tags
    """
    __tablename__ = 'SubRuleToTag'

    sub_rule_id = DB.Column(DB.Integer, DB.ForeignKey('SubRule.id'), primary_key=True)
    tag_id = DB.Column(DB.Integer, DB.ForeignKey('Tag.id'), primary_key=True)
    blacklist = DB.Column(DB.Boolean, default=False, nullable=False)

    def __init__(self, sub_rule_id: int, tag_id: int):
        self.sub_rule_id = sub_rule_id
        self.tag_id = tag_id
