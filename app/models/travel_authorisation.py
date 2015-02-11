from ferris.core.ndb import BasicModel
from google.appengine.ext import ndb

class TravelAuthorisation(BasicModel):
	
    to = ndb.StringProperty(required=True)
    cc = ndb.StringProperty()
    type_of_travel = ndb.StringProperty(required=True)

    # PASSENGER DETAILS
    PD_Name = ndb.StringProperty(required=True)
    PD_Surname = ndb.StringProperty(required=True)
    PD_EmpNumber = ndb.StringProperty()
    PD_Job_Title = ndb.StringProperty()
    PD_Mobile = ndb.StringProperty()
    PD_Email = ndb.StringProperty() # For Int'l Travel Type
    PD_Business_Unit = ndb.StringProperty(required=True)
    PD_Charge_account_number = ndb.StringProperty()
    PD_Date_Completed = ndb.StringProperty(required=True)
    PD_Division = ndb.StringProperty(required=True)
    PD_Charge_CCNum_ProjCode = ndb.StringProperty(required=True)
    PD_Frequent_Flyer_number = ndb.StringProperty()
    
    # FLIGHT DETAILS
    FD_Date = ndb.StringProperty()
    FD_From = ndb.StringProperty()
    FD_To = ndb.StringProperty()
    FD_Req_Dep_Time = ndb.StringProperty()
    FD_Earliest_Dep_Time = ndb.StringProperty()
    FD_Latest_Dep_Time = ndb.StringProperty()
    FD_Latest_Convenient_Arrival_Time = ndb.StringProperty()
    FD_Fare_Type = ndb.StringProperty()
    FD_Indicative_Cost = ndb.StringProperty()
    FD_Total = ndb.StringProperty()
    FD_Special_Instructions = ndb.StringProperty()
    FD_Checked_Baggage = ndb.StringProperty() # For Domestic Travel Type
    FD_Details = ndb.TextProperty() # For Dynamic Rows

    # HOTEL DETAILS
    HD_City_Town = ndb.StringProperty()
    HD_Area = ndb.StringProperty()
    HD_Date_In = ndb.StringProperty()
    HD_Date_Out = ndb.StringProperty()
    HD_Indicative_Cost = ndb.StringProperty()
    HD_Total = ndb.StringProperty()
    #HD_Corporate_Card = ndb.StringProperty()
    HD_Special_Instructions = ndb.StringProperty()
    HD_Details = ndb.TextProperty() # For Dynamic Rows

    # CAR DETAILS
    CD_Pick_Up_Location = ndb.StringProperty()
    CD_Pick_Up_Date = ndb.StringProperty()
    CD_Pick_Up_Time = ndb.StringProperty()
    CD_Drop_Off_Location = ndb.StringProperty()
    CD_Drop_Off_Date = ndb.StringProperty()
    CD_Drop_Off_Time = ndb.StringProperty()
    CD_Indicative_Cost = ndb.StringProperty()
    CD_Total = ndb.StringProperty()
    CD_Special_Instructions = ndb.StringProperty()
    CD_Fastbreak_Number = ndb.StringProperty() # For Int'l Travel Type
    CD_Details = ndb.TextProperty() # For Dynamic Rows
    
    # CAB Charge
    Cab_Charge_Number = ndb.StringProperty()

    # MISCELLANEOUS DETAILS
    ME_AP_Num_of_Travellers = ndb.StringProperty()
    ME_AP_Number_of_Days = ndb.StringProperty()
    ME_AP_Indicative_Cost = ndb.StringProperty()

    ME_B_Num_of_Travellers = ndb.StringProperty()
    ME_B_Number_of_Days = ndb.StringProperty()
    ME_B_Indicative_Cost = ndb.StringProperty()

    ME_D_Num_of_Travellers = ndb.StringProperty()
    ME_D_Number_of_Days = ndb.StringProperty()
    ME_D_Indicative_Cost = ndb.StringProperty()

    ME_Total = ndb.StringProperty()

    # FOREIGN CURRENCY - Requirements Prior to Departure (For Int'l Travel Type)
    FC1_Type_of_Currency = ndb.StringProperty()
    FC1_Num_of_Days_Overseas = ndb.StringProperty()
    FC1_Total_Amount_Requiredy = ndb.StringProperty()

    FC2_Type_of_Currency = ndb.StringProperty()
    FC2_Num_of_Days_Overseas = ndb.StringProperty()
    FC2_Total_Amount_Requiredy = ndb.StringProperty()

    FC3_Type_of_Currency = ndb.StringProperty()
    FC3_Num_of_Days_Overseas = ndb.StringProperty()
    FC3_Total_Amount_Requiredy = ndb.StringProperty()

    # AUTORISATION DETAILS
    AUT_Purpose_of_Travel = ndb.StringProperty(required=True)
    AUT_Total = ndb.StringProperty(required=True)
    AUT_Travel_Authorisation = ndb.StringProperty()
    AUT_ComBy_Name = ndb.StringProperty(required=True)
    AUT_ComBy_Position = ndb.StringProperty(required=True)
    AUT_ComBy_Date = ndb.StringProperty(required=True)
    AUT_AuthBy_Name = ndb.StringProperty(required=True)
    AUT_AuthBy_Position = ndb.StringProperty(required=True)
    AUT_AuthBy_Date = ndb.StringProperty(required=True)
    AUT_Exec_Name = ndb.StringProperty()
    AUT_Exec_Position = ndb.StringProperty()
    AUT_Exec_Date = ndb.StringProperty()
    AUT_SMG_Name = ndb.StringProperty()
    AUT_SMG_Position = ndb.StringProperty()
    AUT_SMG_Date = ndb.StringProperty()
    AUT_Itin_Name = ndb.StringProperty(required=True)
    AUT_Itin_Email = ndb.StringProperty(required=True)
    AUT_Itin_Phone = ndb.StringProperty()
    AUT_Itin_Date = ndb.StringProperty()
    AUT_SecItin_Name = ndb.StringProperty()
    AUT_SecItin_Email = ndb.StringProperty()
    AUT_SecItin_Phone = ndb.StringProperty()
    AUT_SecItin_Date = ndb.StringProperty()

    status = ndb.IntegerProperty(default=1)
