"""
Module containing models for whole API to use.
"""

from flask_restplus import fields
from . import API
from ..hal_field import HaLUrl, UrlData, NestedFields
from ..db_models import STD_STRING_SIZE

WITH_CURIES = API.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

ID = API.model('Id', {
    'id': fields.Integer(min=1),
})

ROOT_LINKS = API.inherit('RootLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_root_resource', absolute=True)),
    'auth': HaLUrl(UrlData('api.auth_authentication_routes', absolute=True)),
    'catalog': HaLUrl(UrlData('api.default_catalog_resource', absolute=True)),
    'search': HaLUrl(UrlData('api.search_search', absolute=True)),
    'doc': HaLUrl(UrlData('api.doc', absolute=True)),
    'spec': HaLUrl(UrlData('api.specs', absolute=True)),
    'lending': HaLUrl(UrlData('api.lending_lending_list', absolute=True)),
})
ROOT_MODEL = API.model('RootModel', {
    '_links': NestedFields(ROOT_LINKS),
})

AUTHENTICATION_ROUTES_LINKS = API.inherit('AuthenticationRoutesLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.auth_authentication_routes', absolute=True)),
    'login': HaLUrl(UrlData('api.auth_login', absolute=True)),
    'guest_login': HaLUrl(UrlData('api.auth_guest_login', absolute=True)),
    'fresh_login': HaLUrl(UrlData('api.auth_fresh_login', absolute=True)),
    'refresh': HaLUrl(UrlData('api.auth_refresh', absolute=True)),
    'check': HaLUrl(UrlData('api.auth_check', absolute=True)),
})
AUTHENTICATION_ROUTES_MODEL = API.model('AuthenticationRoutesModel', {
    '_links': NestedFields(AUTHENTICATION_ROUTES_LINKS),
})

CATALOG_LINKS = API.inherit('CatalogLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_catalog_resource', absolute=True)),
    'items': HaLUrl(UrlData('api.item_item_list', absolute=True)),
    'item_types': HaLUrl(UrlData('api.item_type_item_type_list', absolute=True)),
    'item_tags': HaLUrl(UrlData('api.item_tag_item_tag_list', absolute=True)),
    'attribute_definitions': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list', absolute=True)),
})
CATALOG_MODEL = API.model('CatalogModel', {
    '_links': NestedFields(CATALOG_LINKS),
})

ITEM_TYPE_LINKS = API.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_detail', absolute=True, url_data={'type_id': 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_type_item_type_attributes', url_data={'type_id' : 'id'}, absolute=True)),
    'can_contain': HaLUrl(UrlData('api.item_type_item_type_can_contain_types',
                                  url_data={'type_id' : 'id'}, absolute=True)),
})

ITEM_TYPE_LIST_LINKS = API.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_list', absolute=True)),
})

ITEM_TYPE_POST = API.model('ItemTypePOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'name_schema': fields.String(max_length=STD_STRING_SIZE),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator')),
    'how_to': fields.String(),
})

ITEM_TYPE_PUT = API.inherit('ItemTypePUT', ITEM_TYPE_POST, {
    'lendable': fields.Boolean(default=True),
    'lending_duration': fields.Integer,
})

ITEM_TYPE_GET = API.inherit('ItemType', ITEM_TYPE_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    'id': fields.Integer(),
    '_links': NestedFields(ITEM_TYPE_LINKS),
})

ITEM_TAG_LINKS = API.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_detail', absolute=True, url_data={'tag_id' : 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_tag_item_tag_attributes', url_data={'tag_id' : 'id'}, absolute=True)),
})

ITEM_TAG_LIST_LINKS = API.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_list', absolute=True)),
})

ITEM_TAG_POST = API.model('ItemTagPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'lending_duration': fields.Integer,
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator')),
})

ITEM_TAG_PUT = API.inherit('ItemTagPUT', ITEM_TAG_POST, {
})

ITEM_TAG_GET = API.inherit('ItemTagGET', ITEM_TAG_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    'id': fields.Integer(),
    '_links': NestedFields(ITEM_TAG_LINKS),
})

ATTRIBUTE_DEFINITION_LINKS = API.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_detail', absolute=True,
                           url_data={'definition_id' : 'id'}), required=False),
})

ATTRIBUTE_DEFINITION_LIST_LINKS = API.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list', absolute=True)),
})

ATTRIBUTE_DEFINITION_POST = API.model('AttributeDefinitionPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'type': fields.String(enum=('string', 'integer', 'number', 'boolean')),
    'jsonschema': fields.String(),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator')),
})

ATTRIBUTE_DEFINITION_PUT = API.inherit('AttributeDefinitionPUT', ATTRIBUTE_DEFINITION_POST, {
})

ATTRIBUTE_DEFINITION_GET = API.inherit('AttributeDefinitionGET', ATTRIBUTE_DEFINITION_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    'id': fields.Integer(),
    '_links': NestedFields(ATTRIBUTE_DEFINITION_LINKS),
})

ATTRIBUTE_DEFINITION_VALUES = API.schema_model('AttributeDefinitionVALUE', {
    "type": "array",
    "items": {
        "type": "string",
    }
})

ID = API.model('Id', {
    'id': fields.Integer(min=1, example=1),
})

ID_LIST = API.model('IdList', {
    'ids': fields.List(fields.Integer(min=1, example=1)),
})

ITEM_LINKS = API.inherit('ItemLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_detail', absolute=True, url_data={'item_id' : 'id'}), required=False),
    'tags': HaLUrl(UrlData('api.item_item_item_tags', url_data={'item_id' : 'id'}, absolute=True)),
    'attributes': HaLUrl(UrlData('api.item_item_attribute_list', url_data={'item_id' : 'id'}, absolute=True)),
    'contained_items': HaLUrl(UrlData('api.item_item_contained_items', url_data={'item_id' : 'id'}, absolute=True)),
})

ITEM_LIST_LINKS = API.inherit('ItemLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_list', absolute=True)),
})

ITEM_POST = API.model('ItemPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'type_id': fields.Integer(min=1),
    'lending_duration': fields.Integer(),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator')),
})

ITEM_PUT = API.inherit('ItemPUT', ITEM_POST, {
})

ITEM_GET = API.inherit('ItemGET', ITEM_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    'id': fields.Integer(),
    'type': fields.Nested(ITEM_TYPE_GET),
    'is_currently_lent': fields.Boolean(),
    'lending_id': fields.Integer(),
    '_links': NestedFields(ITEM_LINKS)
})

ATTRIBUTE_LINKS = API.inherit('AttributeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_attribute_detail', absolute=True,
                           url_data={'item_id': 'item_id', 'attribute_definition_id': 'attribute_definition_id'}),
                   required=False),
})

ATTRIBUTE_LIST_LINKS = API.inherit('AttributeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_attribute_list', absolute=True)),
})

ATTRIBUTE_PUT = API.model('AttributePUT', {
    'value': fields.String(),
})

ATTRIBUTE_GET = API.inherit('AttributeGET', ATTRIBUTE_PUT, {
    'attribute_definition_id': fields.Integer(),
    'attribute_definition': fields.Nested(ATTRIBUTE_DEFINITION_GET),
    '_links': NestedFields(ATTRIBUTE_LINKS)
})

LENDING_LINKS = API.inherit('LendingLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.lending_lending_detail', absolute=True,
                           url_data={'lending_id' : 'id'}), required=False),
})

ITEM_LENDING = API.model('ItemLending', {
    'due': fields.DateTime(),
    'item': fields.Nested(ITEM_GET),
})

LENDING_BASIC = API.model('LendingBASIC', {
    'moderator': fields.String(),
    'user': fields.String(),
    'deposit': fields.String(example="Studentenausweis"),
})

LENDING_POST = API.inherit('LendingPOST', LENDING_BASIC, {
    'item_ids': fields.List(fields.Integer(min=1))
})

LENDING_PUT = API.inherit('LendingPUT', LENDING_POST, {
})

LENDING_GET = API.inherit('LendingGET', LENDING_BASIC, ID, {
    '_links': NestedFields(LENDING_LINKS),
    'date': fields.DateTime(),
    'itemLendings': fields.Nested(ITEM_LENDING)
})
