from ferris.core.ndb import ndb, BasicModel
#from google.appengine.api import mail

class DirectorRequest(BasicModel):
    subject = ndb.StringProperty(required=True)
    cc = ndb.TextProperty()
    domain_name = ndb.StringProperty(required=True)
    project_number_name = ndb.StringProperty(required=True)
    details = ndb.TextProperty(required=True)
    special_request = ndb.TextProperty(required=False)
    username = ndb.StringProperty(required=False)
    email_address = ndb.StringProperty(required=False)
    role = ndb.StringProperty(required=False)
    activity = ndb.StringProperty(required=False)
    comment = ndb.TextProperty(required=False)
    status = ndb.IntegerProperty(default=1)

    #DirectorRequestForm = model_form(DirectorRequest, field_args={'status': {'default': 'No need for approval'}})
