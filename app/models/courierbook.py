from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Courierbook(BasicModel):

    #Contact Details
    Full_Name = ndb.StringProperty(required=True)
    Contact_Number = ndb.StringProperty(required=True)
    Requestor_store = ndb.StringProperty()

    #Pick Up Store
    Store_No_Pick_Up = ndb.StringProperty()
    Store_Name_Pick_Up = ndb.StringProperty()
    Address1_Pick_Up = ndb.StringProperty()
    Address2_Pick_Up = ndb.StringProperty()
    Suburb_Pick_Up = ndb.StringProperty()
    State_Pick_Up = ndb.StringProperty()
    Post_Code_Pick_Up = ndb.StringProperty()

    #Destination Store
    Store_No_Dest = ndb.StringProperty()
    Store_Name_Dest = ndb.StringProperty()
    Address1_Dest = ndb.StringProperty()
    Address2_Dest = ndb.StringProperty()
    Suburb_Dest = ndb.StringProperty()
    State_Dest = ndb.StringProperty()
    Post_Code_Dest = ndb.StringProperty()

    #Reason For Courier
    Reason_For_Courier = ndb.StringProperty(required=True)
    Cost_Centre = ndb.StringProperty(required=True)

    #Package Details
    Description_of_Package = ndb.StringProperty()
    Length = ndb.StringProperty(required=True)
    Width = ndb.StringProperty(required=True)
    Height = ndb.StringProperty(required=True)
    Weight = ndb.StringProperty(required=True)
    Quantity = ndb.StringProperty(required=True)
    Insurance_required = ndb.StringProperty(required=True)
    Ready_to_be_collected = ndb.StringProperty(required=True)
    From = ndb.StringProperty(required=True)
    Please_select_the_Courier_Vehicle_size_required = ndb.StringProperty(required=True)