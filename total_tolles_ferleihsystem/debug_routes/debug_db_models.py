"""Module to list debug information for Database Models."""

from inspect import getmembers, isclass, ismodule
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Float, String, Boolean, Date, DateTime
from sqlalchemy.inspection import inspect
from typing import cast, List, Dict, Union
from datetime import datetime, date

from flask import render_template, url_for, abort
from . import debug_blueprint
from .. import DB
from .. import db_models


_data_classes = {}


def _inspect_module(module):
    """Search a Module for Database Models.

    Saves all found modules in _data_classes.

    Arguments:
        module list -- A list of Modules contained inside the Module.
    """
    module_list = getmembers(module, predicate=ismodule)
    classes = getmembers(module, predicate=isclass)
    for (name, cls) in classes:
        if issubclass(cls, DB.Model):
            if cls is not DB.Model:
                _data_classes[name] = cls
    return [mod[1] for mod in module_list]


def _fill_class_dicts():
    """Recursively searche all Modules in data and fill in Taxonomy Classes."""
    global _data_classes
    if not _data_classes:
        stack = []
        visited = set()
        next_module = db_models
        while next_module is not None:
            if next_module in visited:
                next_module = stack.pop()
                continue
            visited.add(next_module)
            stack += _inspect_module(next_module)
            if stack:
                next_module = stack.pop()
            else:
                next_module = None


def _get_class_attributes(attributes, cls, properties, mapper_attrs, table_attributes):
    """Return a filtered list of class attributes.

    Filters Methods, attributes beginning with '_' and foreign key colums (based on '_id' ending).

    Arguments:
        attributes tuple -- Attributes from dir()
        cls -- The class
        properties: List[str] -- list to fill in
        mapper_attrs  -- attributes from sqalchemy inspect
        table_attributes: Dict[str, Union[ColumnProperty, RelationshipProperty]] -- dict to fill in
    """
    for attr in attributes:
        if attr.startswith('_'):
            continue
        if attr.endswith('_id'):
            continue
        if attr in ('metadata', 'query'):
            continue
        var = getattr(cls, attr)
        if callable(var):
            continue
        if isinstance(var, property):
            try:
                attr = '_' + attr
                var = getattr(cls, attr)
                properties.append(attr)
            except AttributeError as err:
                print('could not determin corresponding attribute for property {}'.format(var))
                continue
        if isinstance(var, InstrumentedAttribute):
            var = cast(InstrumentedAttribute, var)
            table_attributes[attr] = mapper_attrs[attr]


def _analyze_db_model(cls):
    """Analyze a db model.

    Analyzes a db Model and returns a summary of the columns etc.
    """
    attributes = dir(cls)

    table_attributes = {}  # type: Dict[str, Union[ColumnProperty, RelationshipProperty]]
    properties = []  # type: List[str]
    mapper_attrs = inspect(cls).attrs

    _get_class_attributes(attributes, cls, properties, mapper_attrs, table_attributes)

    model_fields = []
    attributes_containing_lists = []
    normal_attributes = []
    unknown_attributes = []
    for name, attr in table_attributes.items():
        if isinstance(attr, RelationshipProperty):
            mapper = attr.mapper  # type: Mapper
            if name in properties:
                name = name.lstrip('_')
                attributes_containing_lists.append(name)
                classname = mapper.class_.__name__
                model_fields.append("'{}': fields.List(fields.Raw(description='{}'), default=[]),".format(name, classname))
            else:
                model_fields.append("'{}': fields.Raw(description='{}'),".format(name, mapper.class_.__name__))
                normal_attributes.append((name, mapper.class_))
        if isinstance(attr, ColumnProperty):
            col = attr.columns[0]  # type: Column
            zusatz = ''
            if col.default is not None:
                default = col.default.arg
                if isinstance(default, str):
                    zusatz = "default='{}'".format(default)
                else:
                    zusatz = 'default={}'.format(default)
            if isinstance(col.type, Integer):
                model_fields.append("'{}': fields.Integer({}),".format(name, zusatz))
                if name != 'id':
                    normal_attributes.append((name, int))
            elif isinstance(col.type, Float):
                model_fields.append("'{}': fields.Float({}),".format(name, zusatz))
                normal_attributes.append((name, float))
            elif isinstance(col.type, String):
                model_fields.append("'{}': fields.String({}),".format(name, zusatz))
                normal_attributes.append((name, str))
            elif isinstance(col.type, Boolean):
                model_fields.append("'{}': fields.Boolean({}),".format(name, zusatz))
                normal_attributes.append((name, bool))
            elif isinstance(col.type, Date):
                model_fields.append("'{}': fields.Date({}),".format(name, zusatz))
                normal_attributes.append((name, date))
            else:
                unknown_attributes.append((name, col.type))

    return {
        'model_fields': model_fields,
        'normal_attributes': tuple(normal_attributes),
        'attributes_containing_lists': tuple(attributes_containing_lists),
        'unknown_attributes': tuple(unknown_attributes),
    }


@debug_blueprint.route('/db-models/')
def model_overview():
    _fill_class_dicts()
    return render_template('debug/db-models/all.html',
                           title='Total Tolles Ferleihsystem – DB Models',
                           data_classes=sorted(_data_classes.keys()))


@debug_blueprint.route('/db-models/<string:classname>/')
def model_detail(classname):
    _fill_class_dicts()
    cls = _data_classes.get(classname)
    if cls is None:
        abort(404)
    return render_template('debug/db-models/model.html',
                           title='Total Tolles Ferleihsystem – DB Model <{}>'.format(classname),
                           classname=classname,
                           model_data=_analyze_db_model(cls))
