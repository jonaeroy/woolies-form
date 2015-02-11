from ferris.core.ndb import BasicModel
from ferris.behaviors.searchable import Searchable
from google.appengine.ext import ndb

class Salarysacrifice(BasicModel):

    # Agree/ Disagree Page
    question_1 = ndb.StringProperty()
    question_2 = ndb.StringProperty()
    question_3 = ndb.StringProperty()
    question_4 = ndb.StringProperty()
    question_5 = ndb.StringProperty()
    question_6 = ndb.StringProperty()
    question_7 = ndb.StringProperty()
    question_8 = ndb.StringProperty()

    # Purchase Details page
    full_name = ndb.StringProperty()
    payroll_number = ndb.StringProperty()
    cost_centre = ndb.StringProperty()
    location_name = ndb.StringProperty()
    employment_status = ndb.StringProperty()
    pay_cycle = ndb.StringProperty()
    device_purchase_type = ndb.StringProperty()
    device_description = ndb.StringProperty()
    purchase_amount = ndb.StringProperty()
    gst_amount = ndb.StringProperty()
    purchase_date = ndb.StringProperty()

    # Attachment page
    attachment = ndb.BlobKeyProperty()
    Status = ndb.StringProperty()
    
    @classmethod
    def all(cls):
        return cls.query()

    class Meta:
        behaviors = (Searchable,)