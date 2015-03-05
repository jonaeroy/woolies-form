from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Courierbook(BasicModel):


    #Contact Details
    Full_Name = ndb.StringProperty(required=True)
    Contact_Number = ndb.StringProperty(required=True)
    Requestor_store = ndb.StringProperty()

    #Pick Up Store
    store_no_pick_up = ndb.StringProperty()
    store_name_pick_up = ndb.StringProperty()
    address1_pick_up = ndb.StringProperty()
    address2_pick_up = ndb.StringProperty()
    suburb_pick_up = ndb.StringProperty()
    state_pick_up = ndb.StringProperty()
    post_code_pick_up = ndb.StringProperty()

    #Destination Store
    store_no_dest = ndb.StringProperty()
    store_name_dest = ndb.StringProperty()
    address1_dest = ndb.StringProperty()
    address2_dest = ndb.StringProperty()
    suburb_dest = ndb.StringProperty()
    state_dest = ndb.StringProperty()
    post_code_dest = ndb.StringProperty()

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


    @classmethod
    def create(cls, params):
        item = cls()
        item.populate(**params)
        item.put()
        return item

    @classmethod
    def list_all(cls):
        return cls.query()

    def update(self, params):
        self.populate(**params)
        self.put()


    @classmethod
    def get(cls, key):
        return cls(parent=key)
