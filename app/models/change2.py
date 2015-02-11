from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Change2(BasicModel):

	Comments = ndb.TextProperty()