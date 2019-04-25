"""
This is the module containing the search endpoint.
"""

from flask import request
from flask_restplus import Resource
from flask_jwt_extended import jwt_optional, get_jwt_claims
from sqlalchemy.orm import joinedload
from . import API
from ..db_models.item import Item, ItemToTag, ItemToAttributeDefinition
from ..db_models.tag import Tag
from .models import ITEM_GET
from ..login import UserRole

PATH: str = '/search'
ANS = API.namespace('search', description='The search resource', path=PATH)

@ANS.route('/')
class Search(Resource):
    """
    Search Resource
    """
    @API.doc(security=None)
    @jwt_optional
    @API.param('search', 'the string to search for', type=str, required=False, default='')
    @API.param('limit', 'limit the amount of return values', type=int, required=False, default=1000)
    @API.param('tag', 'Only show items with a tag of the given tag id', type=int, required=False, default='')
    @API.param('attrib', 'Filter the results on specific attributes with a search string in the format: &lt;' +
               'attribute-id&gt;-&lt;search-string&gt;', type=str, required=False, default='')
    @API.param('type', 'Only show items with the given type id', type=int, required=False, default='')
    @API.param('deleted', 'If true also search deleted items', type=bool, required=False, default=False)
    @API.param('lent', 'If true also search lent items', type=bool, required=False, default=False)
    @API.marshal_list_with(ITEM_GET)
    # pylint: disable=R0201
    def get(self):
        """
        The actual search endpoint definition
        """
        search = request.args.get('search', default='', type=str)
        limit = request.args.get('limit', default=1000, type=int)
        tags = request.args.getlist('tag', type=int)
        attributes = request.args.getlist('attrib', type=str)
        item_type = request.args.get('type', default=-1, type=int)
        deleted = request.args.get('deleted', default=False, type=lambda x: x == 'true')
        lent = request.args.get('lent', default=False, type=lambda x: x == 'true')

        search_result = Item.query.options(joinedload('lending'), joinedload("_tags"))

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                search_result = search_result.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                search_result = search_result.filter(Item.visible_for == 'all')

        if search:
            search_array = search.split('|') #TODO make character configurable
            search_condition = Item.name.like('%' + search_array[0].strip() + '%')

            if not tags:
                search_result = search_result.join(ItemToTag, isouter=True).join(Tag, isouter=True)
                search_condition = search_condition | Tag.name.like('%' + search_array[0].strip() + '%')

            search_result = search_result.join(ItemToAttributeDefinition, isouter=True).filter(~ItemToAttributeDefinition.attribute_definition_id.in_([attribute.split('-', 1)[1] for attribute in attributes]))
            search_condition = search_condition | ItemToAttributeDefinition.value.like('%' + search_array[0].strip() + '%')

            for search_string in search_array[1:]:
                search_condition = search_condition | Item.name.like('%' + search_string.strip() + '%')

                if not tags:
                    search_condition = search_condition | Tag.name.like('%' + search_string.strip() + '%')

                search_condition = search_condition | ItemToAttributeDefinition.value.like('%' + search_string.strip() + '%')

            search_result = search_result.filter(search_condition)

        if not deleted:
            search_result = search_result.filter(Item.deleted_time == None)

        if not lent:
            search_result = search_result.filter(Item.lending == None)

        if item_type != -1:
            search_result = search_result.filter(Item.type_id == item_type)

        if tags:
            search_result = search_result.join(ItemToTag)
            search_result = search_result.filter(ItemToTag.tag_id.in_(tags))

        if attributes:
            for attribute in attributes:
                search_result = search_result.join(ItemToAttributeDefinition, aliased=True)
                search_result = search_result.filter(ItemToAttributeDefinition.attribute_definition_id ==
                                                     attribute.split('-', 1)[0])
                search_result = search_result.filter(ItemToAttributeDefinition.value == attribute.split('-', 1)[1])

        return search_result.order_by(Item.name).limit(limit).all()
