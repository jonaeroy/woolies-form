from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Stockreject(BasicModel):

	#Stock Rejected
	To = ndb.StringProperty(required=True)
	CC = ndb.StringProperty(required=True)
	Subject = ndb.StringProperty(required=True)
	Vendor = ndb.StringProperty(required=True)
	Return_Type = ndb.StringProperty(required=True)
	Carrier = ndb.StringProperty(required=True)
	Date_of_Arrival = ndb.DateProperty(auto_now_add=True,required=True)
	Time_of_Rejection = ndb.StringProperty(required=True)
	Product_Other = ndb.TextProperty(required=True)

	#Purchase Order
	Purchase_Order = ndb.StringProperty(required=True)
	Load_Number = ndb.StringProperty(required=True)
	Pallets_Received = ndb.StringProperty(required=True)
	Pallets_Affected = ndb.StringProperty(required=True)
	Cartons_Affected = ndb.StringProperty(required=True)
	Replenishment_Contacted = ndb.StringProperty(required=True,choices=set(["Yes", "No"]))
	Woolworths_Primary_Freight = ndb.StringProperty(required=True,choices=set(["Yes", "No"]))
	Comments = ndb.TextProperty(required=True)
	Attachments = ndb.BlobKeyProperty()
	
	#Contact Details (For Replies)
	From = ndb.StringProperty(required=True)
	Phone = ndb.StringProperty(required=True)
	Fax = ndb.StringProperty()
	Email = ndb.StringProperty(required=True)
	DC = ndb.StringProperty(required=True)

	@classmethod
	def all(cls):
		return cls.query()