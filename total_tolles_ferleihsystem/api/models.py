"""
Module containing models for whole API to use.
"""

from flask_restplus import fields
from . import API
from ..hal_field import HaLUrl, UrlData, NestedFields
from ..db_models import STD_STRING_SIZE


#
# --- Helper Models ---
# These modules are here to provide some consistency across all models.
#

WITH_CURIES = API.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', templated=True,
                             hashtag='!{rel}', name='rel')),
})

ID = API.model('Id', {
    'id': fields.Integer(min=1, example=1, readonly=True, title='Internal Identifier'),
})
ID_LIST = API.model('IdList', {
    'ids': fields.List(fields.Integer(min=1, example=1)),
})

VISIBLE_FOR = API.model('VisibleFor', {
    'visible_for': fields.String(enum=('all', 'moderator', 'administrator'), max_length=STD_STRING_SIZE, title='Access Rights'),
})


#
# --- Root ---
#

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


#
# --- Authentication Routes ---
#

AUTHENTICATION_ROUTES_LINKS = API.inherit('AuthenticationRoutesLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.auth_authentication_routes')),
    'login': HaLUrl(UrlData('api.auth_login')),
    'guest_login': HaLUrl(UrlData('api.auth_guest_login')),
    'fresh_login': HaLUrl(UrlData('api.auth_fresh_login')),
    'refresh': HaLUrl(UrlData('api.auth_refresh')),
    'check': HaLUrl(UrlData('api.auth_check')),
    'settings': HaLUrl(UrlData('api.auth_settings_resource')),
})

AUTHENTICATION_ROUTES_MODEL = API.model('AuthenticationRoutesModel', {
    '_links': NestedFields(AUTHENTICATION_ROUTES_LINKS),
})


#
# --- Catalog ---
#

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


#
# --- Item Type ---
#

ITEM_TYPE_BASIC = API.inherit('ItemTypeBasic', VISIBLE_FOR, {
    'name': fields.String(max_length=STD_STRING_SIZE, title='Name'),
    'name_schema': fields.String(max_length=STD_STRING_SIZE, title='Name Schema'),
    'lendable': fields.Boolean(default=True),
    'lending_duration': fields.Integer(title='Lending Duration'),
    'how_to': fields.String(nullable=True, title='How to'),
})
ITEM_TYPE_LINKS = API.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_detail', url_data={'type_id': 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_type_item_type_attributes', url_data={'type_id' : 'id'})),
    'can_contain': HaLUrl(UrlData('api.item_type_item_type_can_contain_types',
                                  url_data={'type_id' : 'id'})),
})

ITEM_TYPE_POST = API.inherit('ItemTypePOST', ITEM_TYPE_BASIC, {})
ITEM_TYPE_PUT = API.inherit('ItemTypePUT', ITEM_TYPE_BASIC, {})
ITEM_TYPE_GET = API.inherit('ItemType', ITEM_TYPE_BASIC, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ITEM_TYPE_LINKS),
})


#
# --- Item Tag ---
#

ITEM_TAG_BASIC = API.inherit('ItemTagBasic', VISIBLE_FOR, {
    'name': fields.String(max_length=STD_STRING_SIZE, title='Name'),
    'lending_duration': fields.Integer(nullable=True, title='Lending Duration'),
})
ITEM_TAG_LINKS = API.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_detail', url_data={'tag_id' : 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_tag_item_tag_attributes', url_data={'tag_id' : 'id'})),
})

ITEM_TAG_POST = API.inherit('ItemTagPOST', ITEM_TAG_BASIC, {})
ITEM_TAG_PUT = API.inherit('ItemTagPUT', ITEM_TAG_BASIC, {})
ITEM_TAG_GET = API.inherit('ItemTagGET', ITEM_TAG_BASIC, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ITEM_TAG_LINKS),
})


#
# --- Attribute Definition ---
#

ATTRIBUTE_DEFINITION_BASIC = API.inherit('AttributeDefinitionBasic', VISIBLE_FOR, {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'type': fields.String(enum=('string', 'integer', 'number', 'boolean'), max_length=STD_STRING_SIZE),
    'jsonschema': fields.String(nullable=True, default='{\n    \n}', valueType='json', description="""Subset of jsonschema v4

Available Attributes:
* all: "title", "description", "default", "example", "x-nullable", "x-nullValue"
* string: "minLength", "maxLength", "pattern", "enum", "format" ["date"|"date-time"]
* integer: "minimum", "maximum"
* float: "minimum", "maxinum" """),
})
ATTRIBUTE_DEFINITION_LINKS = API.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_detail',
                           url_data={'definition_id' : 'id'}), required=False),
    'autocomplete': HaLUrl(UrlData('api.attribute_definition_attribute_definition_values',
                                   url_data={'definition_id' : 'id'}), required=False),
})

ATTRIBUTE_DEFINITION_POST = API.inherit('AttributeDefinitionPOST', ATTRIBUTE_DEFINITION_BASIC, {})
ATTRIBUTE_DEFINITION_PUT = API.inherit('AttributeDefinitionPUT', ATTRIBUTE_DEFINITION_BASIC, {})
ATTRIBUTE_DEFINITION_GET = API.inherit('AttributeDefinitionGET', ATTRIBUTE_DEFINITION_BASIC, ID, {
    'deleted': fields.Boolean(readonly=True),
    '_links': NestedFields(ATTRIBUTE_DEFINITION_LINKS),
})

ATTRIBUTE_DEFINITION_VALUES = API.schema_model('AttributeDefinitionVALUE', {
    "type": "array",
    "items": {
        "type": "string",
    }
})


#
# --- Item ---
#

ITEM_BASIC = API.inherit('ItemBasic', VISIBLE_FOR, {
    'name': fields.String(max_length=STD_STRING_SIZE, title='Name'),
    'update_name_from_schema': fields.Boolean(default=True, title='Schema Name'),
    'type_id': fields.Integer(min=1, title='Type'),
    'lending_duration': fields.Integer(nullable=True, title='Lending Duration'),
})
ITEM_LINKS = API.inherit('ItemLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_detail', url_data={'item_id' : 'id'}), required=False),
    'tags': HaLUrl(UrlData('api.item_item_item_tags', url_data={'item_id' : 'id'})),
    'attributes': HaLUrl(UrlData('api.item_item_attribute_list', url_data={'item_id' : 'id'})),
    'parent_items': HaLUrl(UrlData('api.item_item_parent_items', url_data={'item_id' : 'id'})),
    'contained_items': HaLUrl(UrlData('api.item_item_contained_items', url_data={'item_id' : 'id'})),
    'files': HaLUrl(UrlData('api.item_item_file', url_data={'item_id' : 'id'}))
})

ITEM_POST = API.inherit('ItemPOST', ITEM_BASIC, {})
ITEM_PUT = API.inherit('ItemPUT', ITEM_BASIC, {})
ITEM_GET = API.inherit('ItemGET', ITEM_BASIC, ID, {
    'deleted': fields.Boolean(readonly=True),
    'type': fields.Nested(ITEM_TYPE_GET),
    'is_currently_lent': fields.Boolean(readonly=True),
    'effective_lending_duration': fields.Integer(readonly=True),
    'lending_id': fields.Integer(readonly=True),
    'due': fields.DateTime(attribute='item_lending.due', readonly=True),
    '_links': NestedFields(ITEM_LINKS)
})


#
# --- Attribute ---
#

ATTRIBUTE_BASIC = API.model('AttributeBasic', {
    'value': fields.String(max_length=STD_STRING_SIZE),
})
ATTRIBUTE_LINKS = API.inherit('AttributeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_item_attribute_detail',
                           url_data={'item_id': 'item_id', 'attribute_definition_id': 'attribute_definition_id'}),
                   required=False),
})

ATTRIBUTE_PUT = API.inherit('AttributePUT', ATTRIBUTE_BASIC, {})
ATTRIBUTE_GET = API.inherit('AttributeGET', ATTRIBUTE_BASIC, {
    'attribute_definition_id': fields.Integer(),
    'attribute_definition': fields.Nested(ATTRIBUTE_DEFINITION_GET),
    '_links': NestedFields(ATTRIBUTE_LINKS)
})


#
# --- FIle ---
#

FILE_BASIC = API.inherit('FileBASIC', VISIBLE_FOR, {
    'name': fields.String(max_length=STD_STRING_SIZE, nullable=True),
    'file_type': fields.String(max_length=20),
    'invalidation': fields.DateTime(nullable=True),
})
FILE_LINKS = API.inherit('FileLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.file_file_detail',
                           url_data={'file_id': 'id'}), required=False),
    'download': HaLUrl(UrlData('api.file_file_data',
                               url_data={'file_hash': 'file_hash'}), required=False),
})

FILE_PUT = API.inherit('FilePUT', FILE_BASIC, {})
FILE_GET = API.inherit('FileGET', FILE_BASIC, ID, {
    'item': fields.Nested(ITEM_GET),
    'file_hash': fields.String(max_length=STD_STRING_SIZE),
    'creation': fields.DateTime(),
    '_links': NestedFields(FILE_LINKS)
})


#
# --- Lending ---
#

LENDING_BASIC = API.model('LendingBASIC', {
    'moderator': fields.String(max_length=STD_STRING_SIZE),
    'user': fields.String(max_length=STD_STRING_SIZE),
    'deposit': fields.String(example="Studentenausweis", max_length=STD_STRING_SIZE),
})
LENDING_ITEM = API.model('LendingItem', {
    'due': fields.DateTime(),
    'item': fields.Nested(ITEM_GET),
})
LENDING_LINKS = API.inherit('LendingLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.lending_lending_detail',
                           url_data={'lending_id' : 'id'}), required=False),
})

LENDING_POST = API.inherit('LendingPOST', LENDING_BASIC, {
    'item_ids': fields.List(fields.Integer(min=1))
})
LENDING_PUT = API.inherit('LendingPUT', LENDING_POST, {})
LENDING_GET = API.inherit('LendingGET', LENDING_BASIC, ID, {
    '_links': NestedFields(LENDING_LINKS),
    'date': fields.DateTime(),
    'item_lendings': fields.Nested(LENDING_ITEM),
})


#
# --- Blacklist ---
#

BLACKLIST_BASIC = API.model('BlacklistBasic', {
    'name': fields.String(max_length=STD_STRING_SIZE),
    'system_wide': fields.Boolean(default=False),
    'reason': fields.String(),
})
BLACKLIST_ITEM_TYPE = API.model('BlacklistItemType', {
    'end_time': fields.DateTime(),
    'reason': fields.String(),
})
BLACKLIST_LINKS = API.inherit('BlacklistLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('', url_data={'id' : 'id'})),
})

BLACKLIST_POST = API.inherit('BlacklistPOST', BLACKLIST_ITEM_TYPE_BASIC, {
    'item_type_id': fields.Integer(min=1, example=1, readonly=True, title='Internal Identifier'),
})
BLACKLIST_PUT = API.inherit('BlacklistPUT', BLACKLIST_BASIC, {})
BLACKLIST_GET = API.inherit('BlacklistGET', BLACKLIST_BASIC, ID, {
    '_links': NestedFields(BLACKLIST_LINKS),
    'blocked_types': fields.Nested(BLACKLIST_ITEM_TYPE)
})
