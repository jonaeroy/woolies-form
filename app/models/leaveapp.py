from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class Leaveapp(BasicModel):

    Line_Manager = ndb.StringProperty(required=True)
    HR_Managers = ndb.StringProperty()
    Payroll_Office = ndb.StringProperty(required=True)
    Location_Name = ndb.StringProperty(required=True)
    Region_Division = ndb.StringProperty(required=True)
    Employee_ID_Number = ndb.StringProperty(required=True)
    Position = ndb.StringProperty(required=True)
    Location_Cost_Center = ndb.StringProperty(required=True)
    Employee_Type = ndb.StringProperty(required=True)
    Pay_Frequency = ndb.StringProperty(required=True)

    LD_TOL_Grp1 = ndb.StringProperty()
    LD_First_Working_DOL1 = ndb.StringProperty()
    LD_Last_Working_DOL1 = ndb.StringProperty()
    LD_Total_Number_WH1 = ndb.StringProperty()
    LD_Date_RTW1 = ndb.StringProperty()

    LD_TOL_Grp2 = ndb.StringProperty()
    LD_First_Working_DOL2 = ndb.StringProperty()
    LD_Last_Working_DOL2 = ndb.StringProperty()
    LD_Total_Number_WH2 = ndb.StringProperty()
    LD_Date_RTW2 = ndb.StringProperty()

    LD_TOL_Grp3 = ndb.StringProperty()
    LD_First_Working_DOL3 = ndb.StringProperty()
    LD_Last_Working_DOL3 = ndb.StringProperty()
    LD_Total_Number_WH3 = ndb.StringProperty()
    LD_Date_RTW3 = ndb.StringProperty()

    LD_TOL_Grp4 = ndb.StringProperty()
    LD_First_Working_DOL4 = ndb.StringProperty()
    LD_Last_Working_DOL4 = ndb.StringProperty()
    LD_Total_Number_WH4 = ndb.StringProperty()
    LD_Date_RTW4 = ndb.StringProperty()

    Full_Time_Question = ndb.StringProperty(required=True)

    Annual_Leave_Only_Hours1 = ndb.StringProperty()
    Annual_Leave_Percentage1 = ndb.StringProperty()

    Annual_Leave_Only_Hours2 = ndb.StringProperty()
    Annual_Leave_Percentage2 = ndb.StringProperty()

    Annual_Leave_Only_Hours3 = ndb.StringProperty()
    Annual_Leave_Percentage3 = ndb.StringProperty()

    Annual_Leave_Only_Hours4 = ndb.StringProperty()
    Annual_Leave_Percentage4 = ndb.StringProperty()

    Public_Holiday_Dates1 = ndb.StringProperty()
    Public_Holiday_Hours1 = ndb.StringProperty()
    Public_Holidays_Percentage1 = ndb.StringProperty()

    Public_Holiday_Dates2 = ndb.StringProperty()
    Public_Holiday_Hours2 = ndb.StringProperty()
    Public_Holidays_Percentage2 = ndb.StringProperty()

    Public_Holiday_Dates3 = ndb.StringProperty()
    Public_Holiday_Hours3 = ndb.StringProperty()
    Public_Holidays_Percentage3 = ndb.StringProperty()

    Public_Holiday_Dates4 = ndb.StringProperty()
    Public_Holiday_Hours4 = ndb.StringProperty()
    Public_Holidays_Percentage4 = ndb.StringProperty()

    RD_On_Mon = ndb.StringProperty()
    RD_On_Tues = ndb.StringProperty()
    RD_On_Wed = ndb.StringProperty()
    RD_On_Thurs = ndb.StringProperty()
    RD_On_Fri = ndb.StringProperty()
    RD_On_Sat = ndb.StringProperty()
    RD_On_Sun = ndb.StringProperty()
    RD_On_Total = ndb.StringProperty()

    RD_Off_Mon = ndb.StringProperty()
    RD_Off_Tues = ndb.StringProperty()
    RD_Off_Wed = ndb.StringProperty()
    RD_Off_Thurs = ndb.StringProperty()
    RD_Off_Fri = ndb.StringProperty()
    RD_Off_Sat = ndb.StringProperty()
    RD_Off_Sun = ndb.StringProperty()
    RD_Off_Total = ndb.StringProperty()

    Status = ndb.IntegerProperty(default=1)
    
    @classmethod
    def all(cls):
        return cls.query()