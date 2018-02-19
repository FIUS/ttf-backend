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
