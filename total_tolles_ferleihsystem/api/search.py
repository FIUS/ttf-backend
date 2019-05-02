"""
This is the module containing the search endpoint.
"""

from flask import request
from flask_restplus import Resource
from flask_jwt_extended import jwt_optional, get_jwt_claims
from sqlalchemy.orm import joinedload
from . import API
from ..db_models.item import Item, ItemToTag, ItemToAttributeDefinition
from ..db_models.itemType import ItemType
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
    @API.param('lendable', 'If true only return lendable items', type=bool, required=False, default=False)
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
        lendable = request.args.get('lendable', default=False, type=lambda x: x == 'true')

        def generate_keyword_search_condition(search_string_param, search_condition_param = None):
            search_string_param = search_string_param.strip()

            if search_condition_param is None:
                search_condition_param = Item.name.like('%' + search_string_param + '%');
            else:
                search_condition_param = search_condition_param | Item.name.like('%' + search_string_param + '%');

            if not tags:
                search_condition_param = search_condition_param | Tag.name.like('%' + search_string_param + '%')

            search_condition_param = search_condition_param | ItemToAttributeDefinition.value.like('%' + search_string_param.strip() + '%')

            return search_condition_param

        search_result = Item.query.options(joinedload('lending'), joinedload("_tags"))

        # auth check
        if UserRole(get_jwt_claims()) != UserRole.ADMIN:
            if UserRole(get_jwt_claims()) == UserRole.MODERATOR:
                search_result = search_result.filter((Item.visible_for == 'all') | (Item.visible_for == 'moderator'))
            else:
                search_result = search_result.filter(Item.visible_for == 'all')

        if search:
            search_array = search.split('|') #TODO make character configurable

            if not tags:
                search_result = search_result.join(ItemToTag, isouter=True).join(Tag, isouter=True)
            search_result = search_result.join(ItemToAttributeDefinition, isouter=True).filter(~ItemToAttributeDefinition.attribute_definition_id.in_([attribute.split('-', 1)[0] for attribute in attributes]))

            search_condition = generate_keyword_search_condition(search_array[0])
            for search_string in search_array[1:]:
                search_condition = generate_keyword_search_condition(search_string, search_condition)

            search_result = search_result.filter(search_condition)

        if not deleted:
            search_result = search_result.filter(Item.deleted_time == None)

        if not lent:
            search_result = search_result.filter(Item.lending == None)

        if lendable:
            search_result = search_result.join(ItemType)
            search_result = search_result.filter(ItemType.lendable == True)

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

                search_value = attribute.split('-', 1)[1].strip()
                if search_value[:2] == '>=':
                    search_result = search_result.filter(ItemToAttributeDefinition.value >= search_value[2:].strip())
                elif search_value[:2] == '<=':
                    search_result = search_result.filter(ItemToAttributeDefinition.value <= search_value[2:].strip())
                elif search_value[:1] == '>':
                    search_result = search_result.filter(ItemToAttributeDefinition.value > search_value[1:].strip())
                elif search_value[:1] == '<':
                    search_result = search_result.filter(ItemToAttributeDefinition.value < search_value[1:].strip())
                else:
                    search_result = search_result.filter(ItemToAttributeDefinition.value == search_value)

        return search_result.order_by(Item.name).limit(limit).all()
