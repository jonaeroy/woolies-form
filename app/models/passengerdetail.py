from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Passengerdetail(BasicModel):

	Surname = ndb.StringProperty(required=True)
	# Requested_By = ndb.StringProperty(required=True)
	# Project_No_ER = ndb.StringProperty(required=True)
	# Banner = ndb.StringProperty(required=True,choices=set(["Supermarkets", "Petrol", "Liquor", "Big W"]))
	# SCO = ndb.StringProperty(required=True,choices=set(["Yes", "No", ""]))
	# Environment = ndb.StringProperty(required=True,choices=set(["Test", "ACPT"]))
	# Start_Date = ndb.DateProperty(required=True)
	# End_Date = ndb.DateProperty(required=True)
	# Software_Version_Level = ndb.StringProperty(required=True)
	# Store_Allocated = ndb.StringProperty(required=True)
	# Test_Purpose_Applications_Required = ndb.TextProperty()