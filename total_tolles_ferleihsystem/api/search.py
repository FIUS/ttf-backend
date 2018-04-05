from flask import request
from flask_restplus import Resource
from . import api
from ..db_models.item import Item, ItemToTag
from ..db_models.tag import Tag
from .models import ITEM_GET

PATH: str = '/search'
ANS = api.namespace('search', description='The search resource', path=PATH)

@ANS.route('/')
class Search(Resource):
    """
    Search Resource
    """
    @api.doc(security=None)
    @api.param('search', 'the string to search for', type=str, required=False, default='')
    @api.param('limit', 'limit the amount of return values', type=int, required=False, default=1000)
    @api.param('tag', 'Only show items with a tag of the given tag id', type=int, required=False, default='')
    @api.param('type', 'Only show items with the given type id', type=int, required=False, default='')
    @api.param('deleted', 'If true also search deleted items', type=bool, required=False, default=False)
    @api.marshal_list_with(ITEM_GET)
    def get(self):
        search_string = request.args.get('search', default='', type=str)
        limit = request.args.get('limit', default=1000, type=int)
        tags = request.args.getlist('tag', type=int)
        item_type = request.args.get('type', default=-1, type=int)
        deleted = request.args.get('deleted', default=False, type=lambda x: x == 'true')

        search_result = Item.query.filter(Item.name.like('%' + search_string + '%'))

        if not deleted:
            search_result = search_result.filter(not Item.deleted)

        if tags:
            search_result = search_result.join(ItemToTag.item)
            search_result = search_result.filter(ItemToTag.tag_id.in_(tags))

        if item_type != -1:
            search_result = search_result.filter(Item.type_id == item_type)

        test = search_result.limit(limit).all()
        print(deleted)

        return test
