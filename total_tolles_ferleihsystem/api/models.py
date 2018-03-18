"""
Module containing models for whole API to use.
"""

from flask_restplus import fields
from . import api
from ..hal_field import HaLUrl, UrlData, NestedFields

WITH_CURIES = api.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

ROOT_LINKS = api.inherit('RootLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_root_resource', absolute=True)),
    'auth': HaLUrl(UrlData('api.auth_authentication_routes', absolute=True)),
    'catalog': HaLUrl(UrlData('api.default_catalog_resource', absolute=True)),
    'doc': HaLUrl(UrlData('api.doc', absolute=True)),
    'spec': HaLUrl(UrlData('api.specs', absolute=True)),
})
ROOT_MODEL = api.model('RootModel', {
    '_links': NestedFields(ROOT_LINKS),
})

AUTHENTICATION_ROUTES_LINKS = api.inherit('AuthenticationRoutesLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.auth_authentication_routes', absolute=True)),
    'login': HaLUrl(UrlData('api.auth_login', absolute=True)),
    'guest_login': HaLUrl(UrlData('api.auth_guest_login', absolute=True)),
    'fresh_login': HaLUrl(UrlData('api.auth_fresh_login', absolute=True)),
    'refresh': HaLUrl(UrlData('api.auth_refresh', absolute=True)),
    'check': HaLUrl(UrlData('api.auth_check', absolute=True)),
})
AUTHENTICATION_ROUTES_MODEL = api.model('AuthenticationRoutesModel', {
    '_links': NestedFields(AUTHENTICATION_ROUTES_LINKS),
})

CATALOG_LINKS = api.inherit('CatalogLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.default_catalog_resource', absolute=True)),
    'item_types': HaLUrl(UrlData('api.item_type_item_type_list', absolute=True)),
    'item_tags': HaLUrl(UrlData('api.item_tag_item_tag_list', absolute=True)),
    'attribute_definitions': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list', absolute=True)),
})
CATALOG_MODEL = api.model('CatalogModel', {
    '_links': NestedFields(CATALOG_LINKS),
})

item_type_links = api.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_detail', absolute=True, url_data={'type_id': 'id'}),
                   required=False),
})

item_type_list_links = api.inherit('ItemTypeLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_type_item_type_list', absolute=True)),
})

item_type_post = api.model('ItemTypePOST', {
    'name': fields.String(),
    'name_schema': fields.String(),
    'visible_for': fields.String(),
    'how_to': fields.String(),
})

item_type_put = api.inherit('ItemTypePUT', item_type_post, {
    'lendable': fields.Boolean(default=True),
})

item_type_get = api.inherit('ItemType', item_type_put, {
    'id': fields.Integer(),
    '_links': NestedFields(item_type_links),
})

ITEM_TAG_LINKS = api.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_detail', absolute=True, url_data={'tag_id' : 'id'}),
                   required=False),
    'attributes': HaLUrl(UrlData('api.item_tag_item_tag_attributes', url_data={'tag_id' : 'id'}, absolute=True)),
})

ITEM_TAG_LIST_LINKS = api.inherit('ItemTagLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.item_tag_item_tag_list', absolute=True)),
})

ITEM_TAG_POST = api.model('ItemTagPOST', {
    'name': fields.String(),
    'lending_duration': fields.Integer,
    'visible_for': fields.String(),
})

ITEM_TAG_PUT = api.inherit('ItemTagPUT', ITEM_TAG_POST, {
})

ITEM_TAG_GET = api.inherit('ItemTagGET', ITEM_TAG_PUT, {
    'id': fields.Integer(),
    '_links': NestedFields(ITEM_TAG_LINKS),
})

ITEM_TAG_GET_ALL = api.inherit('ItemTagGETAll', ITEM_TAG_GET, {
    'deleted': fields.Boolean(),
})

ATTRIBUTE_DEFINITION_LINKS = api.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_detail', absolute=True,
                           url_data={'definition_id' : 'id'}), required=False),
})

ATTRIBUTE_DEFINITION_LIST_LINKS = api.inherit('AttributeDefinitionLinks', WITH_CURIES, {
    'self': HaLUrl(UrlData('api.attribute_definition_attribute_definition_list', absolute=True)),
})

ATTRIBUTE_DEFINITION_POST = api.model('AttributeDefinitionPOST', {
    'name': fields.String(),
    'type': fields.String(),
    'jsonschema': fields.String(),
    'visible_for': fields.String(),
})

ATTRIBUTE_DEFINITION_PUT = api.inherit('AttributeDefinitionPUT', ATTRIBUTE_DEFINITION_POST, {
})

ATTRIBUTE_DEFINITION_GET = api.inherit('AttributeDefinitionGET', ATTRIBUTE_DEFINITION_PUT, {
    'id': fields.Integer(),
    '_links': NestedFields(ATTRIBUTE_DEFINITION_LINKS),
})

ID = api.model('Id', {
    'id': fields.Integer(),
})
