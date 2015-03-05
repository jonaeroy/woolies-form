from ferris.core.ndb import Model
from ferris.behaviors.searchable import Searchable
from google.appengine.ext import ndb

class Costcentre(Model):

    number = ndb.IntegerProperty(required=True)
    store_name = ndb.StringProperty(required=True)

    class Meta:
        behaviors = (Searchable,)

    @classmethod
    def all_costcentres(cls):
        return cls.query().order(cls.number)
