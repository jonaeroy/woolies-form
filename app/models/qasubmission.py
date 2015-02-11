from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Qasubmission(BasicModel):

    To = ndb.StringProperty(required=True)
    Product_Range_Name = ndb.StringProperty(required=True)
    Is_a_product_brief_required = ndb.StringProperty(required=True,
        choices=set(["Yes", "No"]))
    Vendor_Name = ndb.StringProperty(required=True)
    Number_of_SKUs_to_launch = ndb.StringProperty(required=True)
    Trading_Division = ndb.StringProperty(required=True,
        choices=set(["AHL Group Australia", "Big W Australia",
                     "BWS Liquor Australia", "Cellarmasters",
                     "CROMA Electronics India", "Dan Murphy's Australia",
                     "Masters Home Improvement", 
                     "Progressive Enterprises New Zealand", "Thomas Dux Grocer Australia",
                     "Woolworths Liquor", "Woolworths Petrol Australia",
                     "Woolworths Supermarkets Australia", "WW Liquor Group",
                     "All Divisions"]))
    Brand = ndb.StringProperty(required=True)
    Country_of_sale = ndb.StringProperty(required=True,choices=set(["Australia", "New Zealand", "Australia and New Zealand"]))
    Senior_Business_Manager = ndb.StringProperty(required=True)
    Business_Manager = ndb.StringProperty(required=True)
    Sourcing_Manager = ndb.StringProperty(required=True)
    In_Store_Date = ndb.StringProperty(required=True)
    In_DC_Date = ndb.StringProperty(required=True)
    Planned_lst_Ship_Date = ndb.StringProperty(required=True)
    Is_Vendor_Currently_Supplying_to_Woolworths = ndb.StringProperty(required=True,
        choices=set(["Yes", "No"]))
    Is_FPAQ_been_issued = ndb.StringProperty()
    Brief_description_of_range = ndb.StringProperty(required=True)
    Product_details = ndb.StringProperty(required=True)
    Attachment = ndb.BlobKeyProperty()
    QA_number = ndb.IntegerProperty(default=0)

    
    @classmethod
    def all(cls):
        return cls.query()