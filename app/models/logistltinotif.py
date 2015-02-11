from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Logistltinotif(BasicModel):

	To = ndb.StringProperty(required=True)
	CC = ndb.StringProperty()
	Subject = ndb.StringProperty(required=True)
	Site = ndb.StringProperty(required=True)
	Pulse_Event_Number = ndb.StringProperty(required=True)
	Date_of_Incident = ndb.StringProperty(required=True)
	Date_unfit_certificate_issued = ndb.StringProperty(required=True)
	Brief_description_of_incident = ndb.TextProperty(required=True)
	Care_provided_and_status_of_worker = ndb.TextProperty(required=True)
	Consideration_for_other_sites = ndb.TextProperty()
	Any_additional_information = ndb.TextProperty()
	Person_leading_investigation_and_contact_details = ndb.TextProperty(required=True)

	@classmethod
	def all(cls):
		return cls.query()