from ferris.core.ndb import Model
from google.appengine.ext import ndb

class Costcentre(Model):

    number = ndb.IntegerProperty(required=True)
    store_name = ndb.StringProperty(required=True)

    @classmethod
    def all_costcentres(cls):
        return cls.query().order(cls.number)
