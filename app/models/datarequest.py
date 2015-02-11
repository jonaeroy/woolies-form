from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Datarequest(BasicModel):

	Requested_By = ndb.StringProperty(required=True)
	Submission_Date = ndb.DateProperty(auto_now_add=True,required=True)
	Buyer = ndb.StringProperty(required=True)
	Subject = ndb.TextProperty()
	Please_Select_Request_Type = ndb.StringProperty(required=True,choices=set(["Add", "Change", "Delete","Request"]))
	Please_Select_Request_Area = ndb.StringProperty(required=True)
	Attachments = ndb.TextProperty(required=True)
	Comments = ndb.TextProperty()
	Status = ndb.IntegerProperty(default=1)

	@classmethod
	def order_by_created_asc(cls):
		return cls.query().order(cls.created)

	@classmethod
	def order_by_created_desc(cls):
		return cls.query().order(-cls.created)

	@classmethod
	def order_by_created_by_asc(cls):
		return cls.query().order(cls.created_by)

	@classmethod
	def order_by_created_by_desc(cls):
		return cls.query().order(-cls.created_by)

	@classmethod
	def order_by_status_asc(cls):
		return cls.query().order(cls.Status)

	@classmethod
	def order_by_status_desc(cls):
		return cls.query().order(-cls.Status)

	@classmethod
	def all(cls):
		return cls.query()