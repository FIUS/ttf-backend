from collections import OrderedDict
from flask_restplus import marshal
from flask_restplus.fields import Raw, Nested, StringMixin, MarshallingError, get_value, urlparse, urlunparse
from flask import url_for, request
from typing import Dict, List, Union

from . import app


class NestedFields(Nested):

    def __init__(self, model, **kwargs):
        super().__init__(model=model, **kwargs)

    def output(self, key, obj):

        return marshal(obj, self.nested)


class NestedModel():

    def __init__(self, model, attribute: str=None, as_list: bool=False):
        self.model = model
        self.attribute = attribute
        self.as_list = as_list

    @property
    def nested(self):
        return getattr(self.model, 'resolved', self.model)


class EmbeddedFields(Raw):

    def __init__(self, embedded_models: Dict[str, NestedModel], **kwargs):
        self.embedded_models = embedded_models
        super().__init__(**kwargs)

    def nested_model(self, name):
        return self.embedded_models[name].nested

    def output(self, key, obj):
        data = {}

        for name in self.embedded_models:
            key = name if not self.embedded_models[name].attribute else self.embedded_models[name].attribute
            value = get_value(key, obj)
            if value is not None and not (self.embedded_models[name].as_list and (len(value) == 0)):
                data[name] = marshal(value, self.nested_model(name))
        return data

    def schema(self):
        schema = super().schema()
        schema['type'] = 'object'
        schema['required'] = list(self.embedded_models.keys())
        props = OrderedDict()

        for name in self.embedded_models:
            ref = '#/definitions/{0}'.format(self.nested_model(name).name)
            if not self.embedded_models[name].as_list:
                props[name] = {'$ref': ref}
            else:
                props[name] = {'type': 'array', 'items': {'$ref': ref}}
        schema['properties'] = props

        return schema


class UrlData():

    def __init__(self, endpoint: str, absolute=False, scheme=None, url: str=None,
                 title: str=None, name: str=None, templated: bool=False, url_data: dict={},
                 path_variables: list=[], hashtag: str=None):
        self.endpoint = endpoint
        self.absolute = absolute
        self.scheme = scheme
        self._url = url
        self.title = title
        self.name = name
        self.templated = bool(templated)
        self.url_data = url_data
        self.path_variables = ''
        if path_variables:
            self.path_variables = '/'.join('{{{}}}'.format(var) for var in path_variables)
        self.hashtag = ''
        if hashtag is not None:
            self.hashtag = hashtag

    def url(self, obj):
        if self._url:
            return self._url
        url_data = {}
        for key in self.url_data:
            value = get_value(self.url_data[key], obj)
            if value is None:
                app.logger.debug('Could not build url because some provided values were none.\n' +
                                 'UrlParam: "%s", ObjectKey: "%s"',
                                 key, self.url_data[key])
                print(obj)
                return None
            url_data[key] = value
        endpoint = self.endpoint if self.endpoint is not None else request.endpoint
        o = urlparse(url_for(endpoint, _external=self.absolute, **url_data))
        path = ''
        if o.path.endswith('/'):
            path = o.path + self.path_variables
        else:
            path = o.path + '/' + self.path_variables
        if self.absolute:
            scheme = self.scheme if self.scheme is not None else o.scheme
            return urlunparse((scheme, o.netloc, path, "", "", self.hashtag))
        else:
            return urlunparse(("", "", path, "", "", self.hashtag))


class HaLUrl(StringMixin, Raw):
    '''
    A string representation of a Url

    :param str endpoint: Endpoint name. If endpoint is ``None``, ``request.endpoint`` is used instead
    :param bool absolute: If ``True``, ensures that the generated urls will have the hostname included
    :param str scheme: URL scheme specifier (e.g. ``http``, ``https``)
    '''
    __schema_type__ = 'link'

    def __init__(self, url_data: Union[UrlData, List[UrlData]], **kwargs):
        super().__init__(readonly=True, **kwargs)
        self.url_data = url_data
        self.is_list = isinstance(url_data, list)

    def output(self, key, obj):
        output = {}
        if self.is_list:
            output = []
            for data in UrlData:
                output.append(self.generate_link(data, obj))
        else:
            output = self.generate_link(self.url_data, obj)

        return output

    def generate_link(self, url_data: UrlData, obj):
        link = OrderedDict()
        link['templated'] = url_data.templated
        if url_data.title:
            link['title'] = str(url_data.title)
        if url_data.name:
            link['name'] = str(url_data.name)
        try:
            link['href'] = url_data.url(obj)
        except TypeError as te:
            raise MarshallingError(te)
        return link

    def schema(self):
        schema = super().schema()

        link_schema = schema

        if self.is_list:
            link_schema = {}
            schema['type'] = 'array'
            schema['items'] = link_schema

        link_schema['type'] = 'object'
        link_schema['required'] = ['href']
        props = OrderedDict()
        props['href'] = {'type': 'string', 'readOnly': True, 'example': 'http://www.example.com/api'}
        props['templated'] = {'type': 'boolean', 'readOnly': True}
        props['title'] = {'type': 'string', 'readOnly': True}
        props['name'] = {'type': 'string', 'readOnly': True}
        link_schema['properties'] = props

        return schema
