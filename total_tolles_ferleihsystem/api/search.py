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
    @api.marshal_list_with(ITEM_GET)
    def get(self):
        search_string = request.args.get('search', default='', type=str)
        limit = request.args.get('limit', default=1000, type=int)
        tags = request.args.getlist('tag', type=int)
        type = request.args.get('type', default=-1, type=int)

        search_result = Item.query.filter(Item.name.like('%' + search_string + '%'))

        if len(tags) > 0:
            search_result = search_result.join(ItemToTag.item)
            search_result = search_result.filter(ItemToTag.tag_id.in_(tags))

        if type != -1:
            search_result = search_result.filter(Item.type_id == type)

        return search_result.limit(limit).all()
