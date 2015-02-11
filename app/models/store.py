from ferris.core.ndb import Model
from google.appengine.ext import ndb

class Store(Model):
    number = ndb.IntegerProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    address1 = ndb.StringProperty(indexed=False)
    address2 = ndb.StringProperty(indexed=False)
    suburb = ndb.StringProperty(indexed=False)
    state = ndb.StringProperty(indexed=False)
    postcode = ndb.StringProperty(indexed=False)  

    @classmethod
    def all_stores(cls):
        return cls.query().order(cls.number)
