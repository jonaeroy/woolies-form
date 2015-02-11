from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb


class Teststore(BasicModel):

	Project_Name = ndb.StringProperty(required=True)
	Requested_By = ndb.StringProperty(required=True)
	Project_No_ER = ndb.StringProperty(required=True)

	Banner1 = ndb.StringProperty(default=None)
	Sub_Banner1 = ndb.StringProperty(default=None)
	SCO1 = ndb.StringProperty(default=None)
	Environment1 = ndb.StringProperty(default=None)
	Start_Date1 = ndb.StringProperty(default=None)
	End_Date1 = ndb.StringProperty(default=None)
	Software_Version_Level1 = ndb.StringProperty(default=None)
	Store_Allocated1 = ndb.StringProperty(default=None)

	Banner2 = ndb.StringProperty(default=None)
	Sub_Banner2 = ndb.StringProperty(default=None)
	SCO2 = ndb.StringProperty(default=None)
	Environment2 = ndb.StringProperty(default=None)
	Start_Date2 = ndb.StringProperty(default=None)
	End_Date2 = ndb.StringProperty(default=None)
	Software_Version_Level2 = ndb.StringProperty(default=None)
	Store_Allocated2 = ndb.StringProperty(default=None)

	Banner3 = ndb.StringProperty(default=None)
	Sub_Banner3 = ndb.StringProperty(default=None)
	SCO3 = ndb.StringProperty(default=None)
	Environment3 = ndb.StringProperty(default=None)
	Start_Date3 = ndb.StringProperty(default=None)
	End_Date3 = ndb.StringProperty(default=None)
	Software_Version_Level3 = ndb.StringProperty(default=None)
	Store_Allocated3 = ndb.StringProperty(default=None)

	Banner4 = ndb.StringProperty(default=None)
	Sub_Banner4 = ndb.StringProperty(default=None)
	SCO4 = ndb.StringProperty(default=None)
	Environment4 = ndb.StringProperty(default=None)
	Start_Date4 = ndb.StringProperty(default=None)
	End_Date4 = ndb.StringProperty(default=None)
	Software_Version_Level4 = ndb.StringProperty(default=None)
	Store_Allocated4 = ndb.StringProperty(default=None)

	Test_Purpose_Applications_Required = ndb.TextProperty()

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
	def all(cls):
		return cls.query()