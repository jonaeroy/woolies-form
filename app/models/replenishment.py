from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Replenishment(BasicModel):

    # Requestor
    Requested_By = ndb.StringProperty(required=True)
    DateAndTime = ndb.StringProperty(required=True)
    Approver_Details = ndb.StringProperty(required=True)
    Copy_to = ndb.StringProperty()
    Implementer_Details = ndb.StringProperty()
    Change_Type_ddown = ndb.StringProperty(required=True)
    Change_Type_Detail = ndb.TextProperty()
    Risk = ndb.StringProperty(required=True,choices=set(["High", "Medium", "Low"]))
    Priority = ndb.StringProperty(required=True,choices=set(["1", "2", "3", "4"]))
    Back_out_plan = ndb.StringProperty()
    Back_out_plan_details = ndb.StringProperty()
    Change_Type_cbox = ndb.StringProperty(required=True)
    Implementation_date  = ndb.StringProperty(required=True)
    End_date  = ndb.StringProperty()
    Attachment = ndb.BlobKeyProperty()
    ReqComments = ndb.TextProperty()

    # Approver
    Approved = ndb.StringProperty(default="Pending", choices=set(["Pending", "Yes", "No"]))
    Details_if_no = ndb.TextProperty()
    Comments = ndb.TextProperty()

    
    @classmethod
    def all(cls):
        return cls.query()