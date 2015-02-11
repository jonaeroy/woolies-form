from ferris.core.ndb import BasicModel
from ferris.behaviors.searchable import Searchable
from google.appengine.ext import ndb

class Bnld(BasicModel):

    Buyer_or_BAA_Name = ndb.StringProperty(required=True)
    Date = ndb.DateProperty(auto_now_add=True,required=True)
    Merchandise_Manager = ndb.StringProperty(required=True)
    Number_of_Items = ndb.IntegerProperty(required=True)
    All_New_Lines_Passed_Validation = ndb.StringProperty(required=True,choices=set(["Yes", "No", "N/A"]))
    QA_Acceptance = ndb.StringProperty(required=True,choices=set(["Yes", "No", "N/A"]))
    MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines = ndb.StringProperty(required=True,choices=set(["Yes", "No", "N/A"]))
    Include_Any_Comments_Below = ndb.TextProperty()
    Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below = ndb.BlobKeyProperty()
    Status = ndb.IntegerProperty(default=1)
    
    @classmethod
    def all(cls):
        return cls.query()

    class Meta:
        behaviors = (Searchable,)