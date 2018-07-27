"""
Module containing models for whole API to use.
"""

from flask_restplus import fields
from . import API
from ..hal_field import HaLUrl, UrlData, NestedFields
from ..db_models import STD_STRING_SIZE

WITH_CURIES = API.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', templated=True,
                             hashtag='!{rel}', name='rel')),
})

ID = API.model('Id', {
    'id': fields.Integer(min=1, example=1, readonly=True),
})

ROOT_LINKS = API.inherit('RootLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_root_resource')),
    'auth': HaLUrl(UrlData('api.auth_authentication_routes')),
    'catalog': HaLUrl(UrlData('api.default_catalog_resource')),
    'search': HaLUrl(UrlData('api.search_search')),
    'doc': HaLUrl(UrlData('api.doc')),
    'spec': HaLUrl(UrlData('api.specs')),
    'lending': HaLUrl(UrlData('api.lending_lending_list')),
})
ROOT_MODEL = API.model('RootModel', {
    '_links': NestedFields(ROOT_LINKS),
})

AUTHENTICATION_ROUTES_LINKS = API.inherit('AuthenticationRoutesLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.auth_authentication_routes')),
    'login': HaLUrl(UrlData('api.auth_login')),
    'guest_login': HaLUrl(UrlData('api.auth_guest_login')),
    'fresh_login': HaLUrl(UrlData('api.auth_fresh_login')),
    'refresh': HaLUrl(UrlData('api.auth_refresh')),
    'check': HaLUrl(UrlData('api.auth_check')),
})
AUTHENTICATION_ROUTES_MODEL = API.model('AuthenticationRoutesModel', {
    '_links': NestedFields(AUTHENTICATION_ROUTES_LINKS),
})

CATALOG_LINKS = API.inherit('CatalogLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_catalog_resource')),
    'items': HaLUrl(UrlData('api.item_item_list')),
    'item_types': HaLUrl(UrlData('api.item_type_item_type_list')),
    'item_tags': HaLUrl(UrlData('api.item_tag_item_tag_list')),
    'files': HaLUrl(UrlData('api.file_file_list')),
    'attribute_definitions': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list')),
})
CATALOG_MODEL = API.model('CatalogModel', {
    '_links': NestedFields(CATALOG_LINKS),
})

ITEM_TYPE_LINKS = API.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_detail', url_data={'type_id': 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_type_item_type_attributes', url_data={'type_id' : 'id'})),
    'can_contain': HaLUrl(UrlData('api.item_type_item_type_can_contain_types',
                                  url_data={'type_id' : 'id'})),
})

ITEM_TYPE_LIST_LINKS = API.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_list')),
})

ITEM_TYPE_POST = API.model('ItemTypePOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'name_schema': fields.String(max_length=STD_STRING_SIZE),
    'lending_duration': fields.Integer(),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator')),
    'how_to': fields.String(nullable=True, max_length=STD_STRING_SIZE),
})

ITEM_TYPE_PUT = API.inherit('ItemTypePUT', ITEM_TYPE_POST, {
    'lendable': fields.Boolean(default=True),
})

ITEM_TYPE_GET = API.inherit('ItemType', ITEM_TYPE_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ITEM_TYPE_LINKS),
})

ITEM_TAG_LINKS = API.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_detail', url_data={'tag_id' : 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_tag_item_tag_attributes', url_data={'tag_id' : 'id'})),
})

ITEM_TAG_LIST_LINKS = API.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_list')),
})

ITEM_TAG_POST = API.model('ItemTagPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'lending_duration': fields.Integer(nullable=True),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator'), max_length=STD_STRING_SIZE),
})

ITEM_TAG_PUT = API.inherit('ItemTagPUT', ITEM_TAG_POST, {
})

ITEM_TAG_GET = API.inherit('ItemTagGET', ITEM_TAG_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ITEM_TAG_LINKS),
})

ATTRIBUTE_DEFINITION_LINKS = API.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_detail',
                           url_data={'definition_id' : 'id'}), required=False),
    'autocomplete': HaLUrl(UrlData('api.attribute_definition_attribute_definition_values',
                                   url_data={'definition_id' : 'id'}), required=False),
})

ATTRIBUTE_DEFINITION_LIST_LINKS = API.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list')),
})

ATTRIBUTE_DEFINITION_POST = API.model('AttributeDefinitionPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'type': fields.String(enum=('string', 'integer', 'number', 'boolean'), max_length=STD_STRING_SIZE),
    'jsonschema': fields.String(nullable=True, default='{\n    \n}', max_length=STD_STRING_SIZE),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator'), max_length=STD_STRING_SIZE),
})

ATTRIBUTE_DEFINITION_PUT = API.inherit('AttributeDefinitionPUT', ATTRIBUTE_DEFINITION_POST, {
})

ATTRIBUTE_DEFINITION_GET = API.inherit('AttributeDefinitionGET', ATTRIBUTE_DEFINITION_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ATTRIBUTE_DEFINITION_LINKS),
})

ATTRIBUTE_DEFINITION_VALUES = API.schema_model('AttributeDefinitionVALUE', {
    "type": "array",
    "items": {
        "type": "string",
    }
})

ID_LIST = API.model('IdList', {
    'ids': fields.List(fields.Integer(min=1, example=1)),
})

ITEM_LINKS = API.inherit('ItemLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_detail', url_data={'item_id' : 'id'}), required=False),
    'tags': HaLUrl(UrlData('api.item_item_item_tags', url_data={'item_id' : 'id'})),
    'attributes': HaLUrl(UrlData('api.item_item_attribute_list', url_data={'item_id' : 'id'})),
    'contained_items': HaLUrl(UrlData('api.item_item_contained_items', url_data={'item_id' : 'id'})),
    'files': HaLUrl(UrlData('api.item_item_file', url_data={'item_id' : 'id'}))
})

ITEM_LIST_LINKS = API.inherit('ItemLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_list')),
})

ITEM_POST = API.model('ItemPOST', {
    'name': fields.String(max_length=STD_STRING_SIZE, title='Name'),
    'update_name_from_schema': fields.Boolean(default=True, title='Schema Name'),
    'type_id': fields.Integer(min=1, title='Type'),
    'lending_duration': fields.Integer(nullable=True, title='Lending Duration'),
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator'), max_length=STD_STRING_SIZE,
            title='Access Rights'),
})

ITEM_PUT = API.inherit('ItemPUT', ITEM_POST, {
})

ITEM_GET = API.inherit('ItemGET', ITEM_PUT, ID, {
    'deleted': fields.Boolean(readonly=True),
    'type': fields.Nested(ITEM_TYPE_GET),
    'is_currently_lent': fields.Boolean(readonly=True),
    'effective_lending_duration': fields.Integer(readonly=True),
    'lending_id': fields.Integer(readonly=True),
    'due': fields.DateTime(attribute='item_lending.due', readonly=True),
    '_links': NestedFields(ITEM_LINKS)
})

ATTRIBUTE_LINKS = API.inherit('AttributeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_attribute_detail',
                           url_data={'item_id': 'item_id', 'attribute_definition_id': 'attribute_definition_id'}),
                   required=False),
})

ATTRIBUTE_LIST_LINKS = API.inherit('AttributeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_attribute_list')),
})

ATTRIBUTE_PUT = API.model('AttributePUT', {
    'value': fields.String(max_length=STD_STRING_SIZE),
})

ATTRIBUTE_GET = API.inherit('AttributeGET', ATTRIBUTE_PUT, {
    'attribute_definition_id': fields.Integer(),
    'attribute_definition': fields.Nested(ATTRIBUTE_DEFINITION_GET),
    '_links': NestedFields(ATTRIBUTE_LINKS)
})

FILE_LINKS = API.inherit('FileLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.file_file_detail',
                           url_data={'file_id': 'id'}), required=False),
    'download': HaLUrl(UrlData('api.file_file_data',
                               url_data={'file_hash': 'file_hash'}), required=False),
})

FILE_BASIC = API.inherit('FileBASIC', ID, {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'file_type': fields.String(max_length=20),
    'invalidation': fields.DateTime(nullable=True),
})

FILE_GET = API.inherit('FileGET', FILE_BASIC, {
    'item': fields.Nested(ITEM_GET),
    'file_hash': fields.String(max_length=STD_STRING_SIZE),
    'creation': fields.DateTime(),
    'item_id': fields.Integer(min=1),
    '_links': NestedFields(FILE_LINKS)
})

FILE_PUT = API.inherit('FilePUT', FILE_BASIC, {
    'item_id': fields.Integer(min=1)
})

LENDING_LINKS = API.inherit('LendingLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.lending_lending_detail',
                           url_data={'lending_id' : 'id'}), required=False),
})

ITEM_LENDING = API.model('ItemLending', {
    'due': fields.DateTime(),
    'item': fields.Nested(ITEM_GET),
})

LENDING_BASIC = API.model('LendingBASIC', {
    'moderator': fields.String(max_length=STD_STRING_SIZE),
    'user': fields.String(max_length=STD_STRING_SIZE),
    'deposit': fields.String(example="Studentenausweis", max_length=STD_STRING_SIZE),
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
