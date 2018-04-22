"""
This is the module containing the search endpoint.
"""

from flask import request
from flask_restplus import Resource
from flask_jwt_extended import jwt_optional
from . import api
from ..db_models.item import Item, ItemToTag, ItemAttribute
from .models import ITEM_GET

PATH: str = '/search'
ANS = api.namespace('search', description='The search resource', path=PATH)

@ANS.route('/')
class Search(Resource):
    """
    Search Resource
    """
    @api.doc(security=None)
    @jwt_optional
    @api.param('search', 'the string to search for', type=str, required=False, default='')
    @api.param('limit', 'limit the amount of return values', type=int, required=False, default=1000)
    @api.param('tag', 'Only show items with a tag of the given tag id', type=int, required=False, default='')
    @api.param('attrib', 'Filter the results on specific attributes with a search string in the format: &lt;' +
               'attribute-id&gt;-&lt;search-string&gt;', type=str, required=False, default='')
    @api.param('type', 'Only show items with the given type id', type=int, required=False, default='')
    @api.param('deleted', 'If true also search deleted items', type=bool, required=False, default=False)
    @api.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self):
        """
        The actual search endpoint definition
        """
        search_string = request.args.get('search', default='', type=str)
        limit = request.args.get('limit', default=1000, type=int)
        tags = request.args.getlist('tag', type=int)
        attributes = request.args.getlist('attrib', type=str)
        item_type = request.args.get('type', default=-1, type=int)
        deleted = request.args.get('deleted', default=False, type=lambda x: x == 'true')

        search_result = Item.query

        if search_string:
            search_result = search_result.filter(Item.name.like('%' + search_string + '%'))

        if not deleted:
            search_result = search_result.filter(~Item.deleted)

        if tags:
            search_result = search_result.join(ItemToTag.item)
            search_result = search_result.filter(ItemToTag.tag_id.in_(tags))

        if attributes:
            for attribute in attributes:
                search_result = search_result.join(ItemAttribute, aliased=True)
                search_result = search_result.filter(ItemAttribute.item_id == attribute.split('-', 1)[0])
                search_result = search_result.filter(ItemAttribute.value == attribute.split('-', 1)[1])

            # attribute_ids = [attribute.split('-', 1)[0] for attribute in attributes]
            # attribute_values = [attribute.split('-', 1)[1] for attribute in attributes]

            # search_result = search_result.join(ItemAttribute.item)
            # search_filter = None
            # for i in range(len(attributes)):
            #     if search_filter is None:
            #         search_filter = ((ItemAttribute.attribute_definition_id == attribute_ids[i]) &
            #                          (ItemAttribute.value == attribute_values[i]))
            #     else:
            #         search_filter = search_filter | ((ItemAttribute.attribute_definition_id == attribute_ids[i]) &
            #                                          (ItemAttribute.value == attribute_values[i]))
            # search_result = search_result.filter(search_filter)

        if item_type != -1:
            search_result = search_result.filter(Item.type_id == item_type)

        return_value = search_result.limit(limit).all()

        return return_value
