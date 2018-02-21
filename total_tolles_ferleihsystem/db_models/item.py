from .. import db
from . import STD_STRING_SIZE


class Item (db.Model):

    __tablename__ = 'Item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STD_STRING_SIZE), unique=True)
    #TODO type = db.Column(db.Integer, db.foreignKey())
    lending_duration = db.Column(db.Time) #TODO add default value
    delted = db.Column(db.Boolean, default=False)
    visible_for = db.Column(db.String(STD_STRING_SIZE), nullable=True)

    def __init__(self, name: str, lending_duration: int=0, visible_for: str=''):
        self.name = name

        if lending_duration != 0:
           self.lending_duration = lending_duration
           #TODO fix time handling/conversion what ever

        if visible_for != '' and visible_for != None:
            self.visible_for = visible_for


class ItemToItem (db.Model):

    __tablename__ = 'ItemToItem'

    parent_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'), primary_key=True)

    def __init__(self, parent: Item, item: Item):
        self.parent = parent
        self.item = item


class File (db.Model):

    __tablename__ = 'File'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'))
    name = db.Column(db.String(STD_STRING_SIZE))
    path = db.Column(db.String(STD_STRING_SIZE))

    def __init__(self, item: Item, name: str, path: str):
        self.item = item
        self.name = name
        self.path = path
