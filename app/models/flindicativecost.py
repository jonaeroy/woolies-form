from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Flindicativecost(BasicModel):

    fd_from = ndb.StringProperty(required=True)
    fd_to = ndb.StringProperty(required=True)
    fd_ftype = ndb.StringProperty(required=True)
    fd_cost = ndb.StringProperty(required=True)