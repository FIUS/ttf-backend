"""Module containing models for whole API to use."""

from . import api
from ..hal_field import HaLUrl, UrlData, NestedFields

with_curies = api.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

root_links = api.inherit('RootLinks', with_curies, {
    'self': HaLUrl(UrlData('api.default_root_resource', absolute=True)),
    'doc': HaLUrl(UrlData('api.doc', absolute=True)),
    'spec': HaLUrl(UrlData('api.specs', absolute=True)),
    'auth': HaLUrl(UrlData('api.auth_authenticate', absolute=True)),
})

root_model = api.model('RootModel', {
    '_links': NestedFields(root_links),
})

auth_links = api.inherit('AuthLinks', with_curies, {
    'self': HaLUrl(UrlData('api.auth_authentication_routes', absolute=True)),
    'login': HaLUrl(UrlData('api.auth_login', absolute=True)),
    'fresh_login': HaLUrl(UrlData('api.auth_fresh_login', absolute=True)),
    'refresh': HaLUrl(UrlData('api.auth_refresh', absolute=True)),
    'check': HaLUrl(UrlData('api.auth_check', absolute=True)),
})

authentication_routes_model = api.model('AuthenticationRoutesModel', {
    '_links': NestedFields(auth_links),
})
