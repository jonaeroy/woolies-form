from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Googlecalendaremail(BasicModel):

    Calendar_Email = ndb.StringProperty(required=True)
    last_sync = ndb.StringProperty(required=False)
    
    @classmethod
    def all(cls):
        return cls.query()