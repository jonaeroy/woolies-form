from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Poolcarbook(BasicModel):

    Driver_Name = ndb.StringProperty(required=True)
    Driver_Licence_No = ndb.StringProperty(required=True)
    Division_Region  = ndb.StringProperty(required=True)
    Cost_Centre_No = ndb.StringProperty(required=True)
    Authorising_Line_Manager = ndb.StringProperty(required=True)
    Line_Manager_Pos = ndb.StringProperty(required=True)
    Start_Date_Time_Journey = ndb.StringProperty(required=True)
    End_Date_Time_Journey = ndb.StringProperty(required=True)
    Purpose_of_Journey = ndb.TextProperty(required=True)
    
    @classmethod
    def all(cls):
        return cls.query()