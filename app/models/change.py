from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Change(BasicModel):

	Buyer_or_BAA_Name = ndb.StringProperty(required=True)
	Department = ndb.StringProperty(required=True)
	Effective_Date = ndb.StringProperty(required=True)
	Merchandise_Manager = ndb.StringProperty(required=True)
	Submission_Date = ndb.DateProperty(auto_now_add=True,required=True)
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