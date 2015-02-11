from ferris import Controller, scaffold, route_with, route
from ferris.components.pagination import Pagination
from google.appengine.api import users
from ..models.travel_authorisation import TravelAuthorisation
from ferris.core import mail
from ..controllers.utils import Utils
from ..controllers.users import Users
import logging
import json
import datetime
# import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView

from ferris.core.ndb import ndb
from plugins import directory


class TravelAuthorisations(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Drafts, SplitView)
        pagination_limit = 10
        sv_result_variable = 'travel_authorisations'
        sv_status_field = 'status'
        action_form = 'main'

    class Scaffold:
        display_properties = ('created_by', 'created', 'status')

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params, self.request)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

    @route
    def main(self):
        self.context['PAGE_TITLE'] = 'International Travel Requirements'

        # User Info from global address
        userinfodict = directory.get_user_by_email(self.session.get('user_email'))
        user_fullname = None

        if userinfodict:
            user_fullname = userinfodict['fullName']

        if user_fullname is not None:
            name = user_fullname.split(" ")
            if len(name) > 1:
                self.context['first_name'] = name[0]
                self.context['last_name'] = name[1]
            else:
                self.context['first_name'] = name[0]
                self.context['last_name'] = ''

        self.context['user_fullname'] = user_fullname

    @route
    def passenger_details(self):
        self.template_name = 'travel_authorisations/passenger_details.html'

    @route
    def flight_details(self):
        self.template_name = 'travel_authorisations/flight_details.html'

    @route
    def hotel_details(self):
        self.template_name = 'travel_authorisations/hotel_details.html'

    @route
    def car_rental_details(self):
        self.template_name = 'travel_authorisations/car_rental_details.html'

    @route
    def cab_charge(self):
        self.template_name = 'travel_authorisations/cab_charge.html'

    @route
    def miscellaneous_expenses(self):
        self.template_name = 'travel_authorisations/miscellaneous_expenses.html'

    @route
    def authorisation(self):
        self.template_name = 'travel_authorisations/authorisation.html'

    @route
    def list(self):
        usertypekey = self.session.get('user_groups')

        if usertypekey is None:
            usertype = None
        else:
            usertype = self.util.decode_key(usertypekey.urlsafe()).get()

        self.context['usertype'] = usertype

        try:
            self.context['status'] = self.request.params['status']
        except:
            self.context['status'] = 0

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        self.context['frmkey'] = self.session.get(self.name + "_KEY")

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and TravelAuthorisation.created_by or -TravelAuthorisation.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and TravelAuthorisation.status or -TravelAuthorisation.status
        else:
            order = self.request.get('order_by_date') == 'desc' and TravelAuthorisation.created or -TravelAuthorisation.created

        if showAll:
            self.context['travel_authorisations'] = TravelAuthorisation.query().order(order)
        else:
            self.context['travel_authorisations'] = TravelAuthorisation.query(TravelAuthorisation.created_by == users.get_current_user()).order(order)

        self.context['PAGE_TITLE'] = 'Travel Authorisation Requests'
        self.context['isManager'] = self.context.get('user_isManager')
        self.context['sv_travel_authorisations'] = self.context['travel_authorisations']

    @route
    def edit_data(self):

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

        form = self.request.params
        key = form['entity_key']
        # frmkey = form['frmkey']
        item_data = self.util.decode_key(key).get()

        item_data.to = form['to']
        item_data.cc = form['cc']
        item_data.type_of_travel = form['type_of_travel']

        item_data.PD_Name = form['first_names']
        item_data.PD_Surname = form['surname']
        item_data.PD_EmpNumber = form['PD_EmpNumber']
        item_data.PD_Job_Title = form['PD_Job_Title']
        item_data.PD_Mobile = form['PD_Mobile']
        item_data.PD_Email = form['PD_Email']
        item_data.PD_Business_Unit = form['PD_Business_Unit']
        item_data.PD_Charge_account_number = form['PD_Charge_account_number']
        item_data.PD_Date_Completed = form['PD_Date_Completed']
        item_data.PD_Division = form['PD_Division']
        item_data.PD_Charge_CCNum_ProjCode = form['PD_Charge_CCNum_ProjCode']
        item_data.PD_Frequent_Flyer_number = form['PD_Frequent_Flyer_number']

        # FLIGHT DETAILS
        fd_date = self.request.get_all('FD_Date[]')
        fd_from = self.request.get_all('FD_From[]')
        fd_to = self.request.get_all('FD_To[]')
        fd_req_dep_time = self.request.get_all('FD_Req_Dep_Time[]')
        fd_earliest_dep_time = self.request.get_all('FD_Earliest_Dep_Time[]')
        fd_lastest_dep_time = self.request.get_all('FD_Latest_Dep_Time[]')
        fd_latest_conv_arrival_time = self.request.get_all('FD_Latest_Convenient_Arrival_Time[]')
        fd_fare_type = self.request.get_all('FD_Fare_Type[]')
        fd_indicative_cost = self.request.get_all('FD_Indicative_Cost[]')

        fd_details = []

        for count in range(len(fd_date)):
            fd_data = {}

            fd_data['fd_date'] = Utils.html_escape(fd_date[count])
            fd_data['fd_from'] = Utils.html_escape(fd_from[count])
            fd_data['fd_to'] = Utils.html_escape(fd_to[count])
            fd_data['fd_req_dep_time'] = Utils.html_escape(fd_req_dep_time[count])
            fd_data['fd_earliest_dep_time'] = Utils.html_escape(fd_earliest_dep_time[count])
            fd_data['fd_lastest_dep_time'] = Utils.html_escape(fd_lastest_dep_time[count])
            fd_data['fd_latest_conv_arrival_time'] = Utils.html_escape(fd_latest_conv_arrival_time[count])
            fd_data['fd_fare_type'] = Utils.html_escape(fd_fare_type[count])
            fd_data['fd_indicative_cost'] = Utils.html_escape(fd_indicative_cost[count])

            fd_details.append(fd_data)

        FD_Details = json.dumps(fd_details)

        # HOTEL DETAILS
        hd_city_town = self.request.get_all('HD_City_Town[]')
        hd_area = self.request.get_all('HD_Area[]')
        hd_date_in = self.request.get_all('HD_Date_In[]')
        hd_date_out = self.request.get_all('HD_Date_Out[]')
        hd_indicative_cost = self.request.get_all('HD_Indicative_Cost[]')

        hd_details = []

        for count in range(len(hd_city_town)):
            hd_data = {}

            hd_data['hd_city_town'] = Utils.html_escape(hd_city_town[count])
            hd_data['hd_area'] = Utils.html_escape(hd_area[count])
            hd_data['hd_date_in'] = Utils.html_escape(hd_date_in[count])
            hd_data['hd_date_out'] = Utils.html_escape(hd_date_out[count])
            hd_data['hd_indicative_cost'] = Utils.html_escape(hd_indicative_cost[count])

            hd_details.append(hd_data)

        HD_Details = json.dumps(hd_details)

        # CAR RENTAL DETAILS
        cd_pickup_location = self.request.get_all('CD_Pick_Up_Location[]')
        cd_pick_up_date = self.request.get_all('CD_Pick_Up_Date[]')
        cd_pickup_time = self.request.get_all('CD_Pick_Up_Time[]')
        cd_drop_off_location = self.request.get_all('CD_Drop_Off_Location[]')
        cd_drop_off_date = self.request.get_all('CD_Drop_Off_Date[]')
        cd_drop_off_time = self.request.get_all('CD_Drop_Off_Time[]')
        cd_indicative_cost = self.request.get_all('CD_Indicative_Cost[]')

        cd_details = []

        for count in range(len(cd_pickup_location)):
            cd_data = {}
            cd_data['cd_pickup_location'] = Utils.html_escape(cd_pickup_location[count])
            cd_data['cd_pick_up_date'] = Utils.html_escape(cd_pick_up_date[count])
            cd_data['cd_pickup_time'] = Utils.html_escape(cd_pickup_time[count])
            cd_data['cd_drop_off_location'] = Utils.html_escape(cd_drop_off_location[count])
            cd_data['cd_drop_off_date'] = Utils.html_escape(cd_drop_off_date[count])
            cd_data['cd_drop_off_time'] = Utils.html_escape(cd_drop_off_time[count])
            cd_data['cd_indicative_cost'] = Utils.html_escape(cd_indicative_cost[count])

            cd_details.append(cd_data)

        CD_Details = json.dumps(cd_details)

        # ALL of these fields are in JSON code of FD_Details
        # item_data.FD_Date = form['FD_Date']
        # item_data.FD_From = form['FD_From']
        # item_data.FD_To = form['FD_To']
        # item_data.FD_Req_Dep_Time = form['FD_Req_Dep_Time']
        # item_data.FD_Earliest_Dep_Time = form['FD_Earliest_Dep_Time']
        # item_data.FD_Latest_Dep_Time = form['FD_Latest_Dep_Time']
        # item_data.FD_Latest_Convenient_Arrival_Time = form['FD_Latest_Convenient_Arrival_Time']
        # item_data.FD_Fare_Type = form['FD_Fare_Type']
        # item_data.FD_Indicative_Cost = form['FD_Indicative_Cost']

        item_data.FD_Total = form['FD_Total']
        item_data.FD_Special_Instructions = form['FD_Special_Instructions']
        item_data.FD_Checked_Baggage = form['FD_Checked_Baggage']
        item_data.FD_Details = FD_Details

        # ALL of these fields are in JSON code of HD_Details
        # item_data.HD_City_Town = form['HD_City_Town']
        # item_data.HD_Area = form['HD_Area']
        # item_data.HD_Date_In = form['HD_Date_In']
        # item_data.HD_Date_Out = form['HD_Date_Out']
        # item_data.HD_Indicative_Cost = form['HD_Indicative_Cost']
        item_data.HD_Total = form['HD_Total']
        item_data.HD_Special_Instructions = form['HD_Special_Instructions']
        item_data.HD_Details = HD_Details

        # ALL of these fields are in JSON code of CD_Details
        # item_data.CD_Pick_Up_Location = form['CD_Pick_Up_Location']
        # item_data.CD_Pick_Up_Date = form['CD_Pick_Up_Date']
        # item_data.CD_Pick_Up_Time = form['CD_Pick_Up_Time']
        # item_data.CD_Drop_Off_Location = form['CD_Drop_Off_Location']
        # item_data.CD_Drop_Off_Date = form['CD_Drop_Off_Date']
        # item_data.CD_Drop_Off_Time = form['CD_Drop_Off_Time']
        # item_data.CD_Indicative_Cost = form['CD_Indicative_Cost']
        item_data.CD_Total = form['CD_Total']
        item_data.CD_Special_Instructions = form['CD_Special_Instructions']
        item_data.CD_Fastbreak_Number = form['CD_Fastbreak_Number']
        item_data.CD_Details = CD_Details

        item_data.Cab_Charge_Number = form['Cab_Charge_Number']

        item_data.ME_AP_Num_of_Travellers = form['ME_AP_Num_of_Travellers']
        item_data.ME_AP_Number_of_Days = form['ME_AP_Number_of_Days']
        item_data.ME_AP_Indicative_Cost = form['ME_AP_Indicative_Cost']
        item_data.ME_B_Num_of_Travellers = form['ME_B_Num_of_Travellers']
        item_data.ME_B_Number_of_Days = form['ME_B_Number_of_Days']
        item_data.ME_B_Indicative_Cost = form['ME_B_Indicative_Cost']
        item_data.ME_D_Num_of_Travellers = form['ME_D_Num_of_Travellers']
        item_data.ME_D_Number_of_Days = form['ME_D_Number_of_Days']
        item_data.ME_D_Indicative_Cost = form['ME_D_Indicative_Cost']
        item_data.ME_Total = form['ME_Total']

        item_data.FC1_Type_of_Currency = form['FC1_Type_of_Currency']
        item_data.FC1_Num_of_Days_Overseas = form['FC1_Num_of_Days_Overseas']
        item_data.FC1_Total_Amount_Requiredy = form['FC1_Total_Amount_Requiredy']
        item_data.FC2_Type_of_Currency = form['FC2_Type_of_Currency']
        item_data.FC2_Num_of_Days_Overseas = form['FC2_Num_of_Days_Overseas']
        item_data.FC2_Total_Amount_Requiredy = form['FC2_Total_Amount_Requiredy']
        item_data.FC3_Type_of_Currency = form['FC3_Type_of_Currency']
        item_data.FC3_Num_of_Days_Overseas = form['FC3_Num_of_Days_Overseas']
        item_data.FC3_Total_Amount_Requiredy = form['FC3_Total_Amount_Requiredy']

        item_data.AUT_Purpose_of_Travel = form['AUT_Purpose_of_Travel']
        item_data.AUT_Total = form['AUT_Total']
        item_data.AUT_Travel_Authorisation = form['AUT_Travel_Authorisation']
        item_data.AUT_ComBy_Name = form['AUT_ComBy_Name']
        item_data.AUT_ComBy_Position = form['AUT_ComBy_Position']
        item_data.AUT_ComBy_Date = form['AUT_ComBy_Date']
        item_data.AUT_AuthBy_Name = form['AUT_AuthBy_Name']
        item_data.AUT_AuthBy_Position = form['AUT_AuthBy_Position']
        item_data.AUT_AuthBy_Date = form['AUT_AuthBy_Date']
        item_data.AUT_Exec_Name = form['AUT_Exec_Name']
        item_data.AUT_Exec_Position = form['AUT_Exec_Position']
        item_data.AUT_Exec_Date = form['AUT_Exec_Date']
        # item_data.AUT_SMG_Name = form['AUT_SMG_Name']
        # item_data.AUT_SMG_Position = form['AUT_SMG_Position']
        # item_data.AUT_SMG_Date = form['AUT_SMG_Date']
        item_data.AUT_Itin_Name = form['AUT_Itin_Name']
        item_data.AUT_Itin_Email = form['AUT_Itin_Email']
        item_data.AUT_Itin_Phone = form['AUT_Itin_Phone']
        item_data.AUT_Itin_Date = form['AUT_Itin_Date']
        item_data.AUT_SecItin_Name = form['AUT_SecItin_Name']
        item_data.AUT_SecItin_Email = form['AUT_SecItin_Email']
        item_data.AUT_SecItin_Phone = form['AUT_SecItin_Phone']
        item_data.AUT_SecItin_Date = form['AUT_SecItin_Date']

        # item_data.status = int(form['status'])

        entity = item_data.put()

        # Send email after editing #
        status = 'Edited'
        additional_comments = 'N/A'
        subject = "Change in Travel Authorisation Request Notification"

        item = entity.get()

        to = item.to
        cc = item.cc

        recipients = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
        #recipients += to
        domain_path = self.session.get('DOMAIN_PATH')

        if cc is None or str(cc) == "":
            cc = None

        cc_app_rej = None
        form_key = self.request.get('FORM_KEY')
        encoded_param = "?key=" + form_key

        # Create approve/reject link
        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'approve')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject')

        self.sendMail(status, item, additional_comments, recipients, subject, domain_path, encoded_param, cc_app_rej, approve_link, reject_link)
        self.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param, cc)

        # return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))
        return "Done"

    @route_with(template='/travel_authorisations/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        _list = []
        assignees = None

        if entity:
            approver_group_key = entity.first_level_manager.get().key.urlsafe()

            if approver_group_key is not None:
                assignees = Users.get_user_list_by_group(approver_group_key)
                assignees = assignees.replace(" ","")

        if assignees is not None:
            _list = assignees.split(";")

        if user in _list:

            item = self.util.decode_key(entity_key).get()
            domain_path = self.session.get('DOMAIN_PATH')
            encoded_param = "?key=" + form_key
            additional_comments = 'N/A'

            if flag == 'approve':
                status = 3
                subject = "Travel Authorisation Request Approval Notification"
                form_status = "Approved"
            elif flag == 'reject':
                status = 4
                subject = "Travel Authorisation Request Rejection Notification"
                form_status = "Rejected"

            if item:
                if item.status == 1:
                    item.status = status
                    item.put()

                    cc = item.cc

                    if cc is None or str(cc) == "":
                        cc = None

                    # Send Email
                    to = str(item.created_by)
                    self.sendMail(form_status, item, additional_comments, to, subject, domain_path, encoded_param, cc)

                    # Redirect
                    return self.redirect(self.uri(action='list', key=form_key, status=status))
            else:
                return 404

            if item.status > 2:

                #return "<br><br><br><center><b>This request has been Approved or Rejected. Back to <a href='http://" + str(domain_path) + "/travel_authorisations" + str(encoded_param) + "&status=all'>list.</a></b></center>"
                return self.components.split_view.already_approved(form_key)

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['key']  = key
        self.context['frmkey']  = self.request.params['frmkey']
        self.context['fd_details'] = json.loads(item.FD_Details)
        self.context['cd_details'] = json.loads(item.CD_Details)
        self.context['hd_details'] = json.loads(item.HD_Details)

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/travel_authorisations/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.status)

    @route
    def delete(self, key):
        result = self.util.decode_key(key).get()
        result.key.delete()
        frmkey = self.request.params['frmkey']
        status = self.request.params['status']
        return self.redirect(self.uri(action='delete_suc', key=frmkey, status=status))

    @route
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        self.context['status'] = self.request.params['status']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self, key):
        is_creator = False

        result = self.util.decode_key(key).get()

        if str(users.get_current_user()) == str(result.created_by):
            is_creator = True

        self.context['frmkey'] = self.request.params['frmkey']
        self.context['item'] = result

        # PASSENGER DETAILS
        self.context['PD_Name'] = result.PD_Name
        self.context['PD_Surname'] = result.PD_Surname
        self.context['PD_EmpNumber'] = result.PD_EmpNumber
        self.context['PD_Job_Title'] = result.PD_Job_Title
        self.context['PD_Mobile'] = result.PD_Mobile
        self.context['PD_Email'] = result.PD_Email
        self.context['PD_Business_Unit'] = result.PD_Business_Unit
        self.context['PD_Charge_account_number'] = result.PD_Charge_account_number
        self.context['PD_Date_Completed'] = result.PD_Date_Completed
        self.context['PD_Charge_CCNum_ProjCode'] = result.PD_Charge_CCNum_ProjCode
        self.context['PD_Frequent_Flyer_number'] = result.PD_Frequent_Flyer_number
        self.context['PD_Division'] = result.PD_Division

        # FLIGHT DETAILS
        self.context['FD_Details'] = json.loads(result.FD_Details)
        self.context['FD_Checked_Baggage'] = result.FD_Checked_Baggage
        self.context['FD_Special_Instructions'] = result.FD_Special_Instructions
        self.context['FD_Total'] = result.FD_Total

        # HOTEL DETAILS
        self.context['HD_Details'] = json.loads(result.HD_Details)
        #self.context['HD_Corporate_Card'] = result.HD_Corporate_Card
        self.context['HD_Special_Instructions'] = result.HD_Special_Instructions
        self.context['HD_Total'] = result.HD_Total

        # HOTEL DETAILS
        self.context['CD_Details'] = json.loads(result.CD_Details)
        self.context['CD_Fastbreak_Number'] = result.CD_Fastbreak_Number
        self.context['CD_Special_Instructions'] = result.CD_Special_Instructions
        self.context['CD_Total'] = result.CD_Total

        # CAB CHARGE
        self.context['Cab_Charge_Number'] = result.Cab_Charge_Number

        # MISCELLANEOUS EXPENSES
        self.context['ME_AP_Num_of_Travellers'] = result.ME_AP_Num_of_Travellers
        self.context['ME_AP_Number_of_Days'] = result.ME_AP_Number_of_Days
        self.context['ME_AP_Indicative_Cost'] = result.ME_AP_Indicative_Cost
        self.context['ME_B_Num_of_Travellers'] = result.ME_B_Num_of_Travellers
        self.context['ME_B_Number_of_Days'] = result.ME_B_Number_of_Days
        self.context['ME_B_Indicative_Cost'] = result.ME_B_Indicative_Cost
        self.context['ME_D_Num_of_Travellers'] = result.ME_D_Num_of_Travellers
        self.context['ME_D_Number_of_Days'] = result.ME_D_Number_of_Days
        self.context['ME_D_Indicative_Cost'] = result.ME_D_Indicative_Cost
        self.context['ME_Total'] = result.ME_Total

        # REQUIREMENTS PRIOR TO DEPARTURE
        self.context['FC1_Type_of_Currency'] = result.FC1_Type_of_Currency
        self.context['FC1_Num_of_Days_Overseas'] = result.FC1_Num_of_Days_Overseas
        self.context['FC1_Total_Amount_Requiredy'] = result.FC1_Total_Amount_Requiredy
        self.context['FC2_Type_of_Currency'] = result.FC2_Type_of_Currency
        self.context['FC2_Num_of_Days_Overseas'] = result.FC2_Num_of_Days_Overseas
        self.context['FC2_Total_Amount_Requiredy'] = result.FC2_Total_Amount_Requiredy
        self.context['FC3_Type_of_Currency'] = result.FC3_Type_of_Currency
        self.context['FC3_Num_of_Days_Overseas'] = result.FC3_Num_of_Days_Overseas
        self.context['FC3_Total_Amount_Requiredy'] = result.FC3_Total_Amount_Requiredy

        # AUTHORISATION
        self.context['AUT_Purpose_of_Travel'] = result.AUT_Purpose_of_Travel
        self.context['AUT_Total'] = result.AUT_Total
        self.context['AUT_Travel_Authorisation'] = result.AUT_Travel_Authorisation

        self.context['AUT_ComBy_Name'] = result.AUT_ComBy_Name
        self.context['AUT_ComBy_Position'] = result.AUT_ComBy_Position
        self.context['AUT_ComBy_Date'] = result.AUT_ComBy_Date
        self.context['AUT_AuthBy_Name'] = result.AUT_AuthBy_Name
        self.context['AUT_AuthBy_Position'] = result.AUT_AuthBy_Position
        self.context['AUT_AuthBy_Date'] = result.AUT_AuthBy_Date
        self.context['AUT_Exec_Name'] = result.AUT_Exec_Name
        self.context['AUT_Exec_Position'] = result.AUT_Exec_Position
        self.context['AUT_Exec_Date'] = result.AUT_Exec_Date
        # self.context['AUT_SMG_Name'] = result.AUT_SMG_Name
        # self.context['AUT_SMG_Position'] = result.AUT_SMG_Position
        # self.context['AUT_SMG_Date'] = result.AUT_SMG_Date

        self.context['AUT_Itin_Name'] = result.AUT_Itin_Name
        self.context['AUT_Itin_Email'] = result.AUT_Itin_Email
        self.context['AUT_Itin_Phone'] = result.AUT_Itin_Phone
        self.context['AUT_Itin_Date'] = result.AUT_Itin_Date
        self.context['AUT_SecItin_Name'] = result.AUT_SecItin_Name
        self.context['AUT_SecItin_Email'] = result.AUT_SecItin_Email
        self.context['AUT_SecItin_Phone'] = result.AUT_SecItin_Phone
        self.context['AUT_SecItin_Date'] = result.AUT_SecItin_Date

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Travel Authorisation Request View'
        self.context['is_creator'] = is_creator

    @route
    def sendNotif(self):
        form = self.request.params

        action = form['action']
        additional_comments = form['additional_comments']
        keyid = form['keyid']

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        result = self.util.decode_key(keyid).get()
        domain_path = self.session.get('DOMAIN_PATH')
        subject = 'Travel Authorisation Request Notification'

        cc = result.cc

        if cc is None or str(cc) == "":
            cc = None

        if (action == "approve"):
            result.status = 3
            result.put()
            form_status = "Approved"
            subject = "Travel Authorisation Request Approval Notification"
            recipient = result.to
            to = str(result.created_by) + ";" + recipient
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param, cc)
        elif (action == "reject"):
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Travel Authorisation Request Rejection Notification"
            recipient = result.to
            to = str(result.created_by) + ";" + recipient
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param, cc)

        return self.redirect(self.uri(action='list', key=form_key))

    @classmethod
    def sendMail(self, status, resource, additional_comments, to, subject, domain_path, encoded_param, cc, approve_link='#', reject_link='#'):

        user = str(users.get_current_user())
        domain_path = str(domain_path)
        date_time = Utils.localize_datetime(datetime.datetime.now())

        # PASSENGER DETAILS
        PD_Name = resource.PD_Name
        PD_Surname = resource.PD_Surname
        PD_Job_Title = resource.PD_Job_Title
        PD_EmpNumber = resource.PD_EmpNumber
        PD_Mobile = resource.PD_Mobile
        PD_Email = resource.PD_Email
        PD_Business_Unit = resource.PD_Business_Unit
        PD_Charge_account_number = resource.PD_Charge_account_number
        PD_Date_Completed = resource.PD_Date_Completed
        PD_Charge_CCNum_ProjCode = resource.PD_Charge_CCNum_ProjCode
        PD_Frequent_Flyer_number = resource.PD_Frequent_Flyer_number
        PD_Division = resource.PD_Division

        # FLIGHT DETAILS
        FD_Details = json.loads(resource.FD_Details)
        FD_Checked_Baggage = resource.FD_Checked_Baggage
        FD_Special_Instructions = resource.FD_Special_Instructions
        FD_Total = resource.FD_Total

        # HOTEL DETAILS
        HD_Details = json.loads(resource.HD_Details)
        #HD_Corporate_Card = resource.HD_Corporate_Card
        HD_Special_Instructions = resource.HD_Special_Instructions
        HD_Total = resource.HD_Total

        # CAR RENTAL DETAILS
        CD_Details = json.loads(resource.CD_Details)
        CD_Fastbreak_Number = resource.CD_Fastbreak_Number
        CD_Special_Instructions = resource.CD_Special_Instructions
        CD_Total = resource.CD_Total

        # CAB CHARGE
        Cab_Charge_Number = resource.Cab_Charge_Number

        # MISCELLANEOUS EXPENSES
        ME_AP_Num_of_Travellers = resource.ME_AP_Num_of_Travellers
        ME_AP_Number_of_Days = resource.ME_AP_Number_of_Days
        ME_AP_Indicative_Cost = resource.ME_AP_Indicative_Cost
        ME_B_Num_of_Travellers = resource.ME_B_Num_of_Travellers
        ME_B_Number_of_Days = resource.ME_B_Number_of_Days
        ME_B_Indicative_Cost = resource.ME_B_Indicative_Cost
        ME_D_Num_of_Travellers = resource.ME_D_Num_of_Travellers
        ME_D_Number_of_Days = resource.ME_D_Number_of_Days
        ME_D_Indicative_Cost = resource.ME_D_Indicative_Cost
        ME_Total = resource.ME_Total

        # REQUIREMENTS PRIOR TO DEPARTURE
        FC1_Type_of_Currency = resource.FC1_Type_of_Currency
        FC1_Num_of_Days_Overseas = resource.FC1_Num_of_Days_Overseas
        FC1_Total_Amount_Requiredy = resource.FC1_Total_Amount_Requiredy
        FC2_Type_of_Currency = resource.FC2_Type_of_Currency
        FC2_Num_of_Days_Overseas = resource.FC2_Num_of_Days_Overseas
        FC2_Total_Amount_Requiredy = resource.FC2_Total_Amount_Requiredy
        FC3_Type_of_Currency = resource.FC3_Type_of_Currency
        FC3_Num_of_Days_Overseas = resource.FC3_Num_of_Days_Overseas
        FC3_Total_Amount_Requiredy = resource.FC3_Total_Amount_Requiredy

        # AUTHORISATION
        AUT_Purpose_of_Travel = resource.AUT_Purpose_of_Travel
        AUT_Total = resource.AUT_Total
        AUT_Travel_Authorisation = resource.AUT_Travel_Authorisation

        AUT_ComBy_Name = resource.AUT_ComBy_Name
        AUT_ComBy_Position = resource.AUT_ComBy_Position
        AUT_ComBy_Date = resource.AUT_ComBy_Date
        AUT_AuthBy_Name = resource.AUT_AuthBy_Name
        AUT_AuthBy_Position = resource.AUT_AuthBy_Position
        AUT_AuthBy_Date = resource.AUT_AuthBy_Date
        AUT_Exec_Name = resource.AUT_Exec_Name
        AUT_Exec_Position = resource.AUT_Exec_Position
        AUT_Exec_Date = resource.AUT_Exec_Date
        # AUT_SMG_Name = resource.AUT_SMG_Name
        # AUT_SMG_Position = resource.AUT_SMG_Position
        # AUT_SMG_Date = resource.AUT_SMG_Date

        AUT_Itin_Name = resource.AUT_Itin_Name
        AUT_Itin_Email = resource.AUT_Itin_Email
        AUT_Itin_Phone = resource.AUT_Itin_Phone
        AUT_Itin_Date = resource.AUT_Itin_Date
        AUT_SecItin_Name = resource.AUT_SecItin_Name
        AUT_SecItin_Email = resource.AUT_SecItin_Email
        AUT_SecItin_Phone = resource.AUT_SecItin_Phone
        AUT_SecItin_Date = resource.AUT_SecItin_Date

        fd_details_str = ""
        hd_details_str = ""
        cd_details_str = ""

        for detail in FD_Details:
                fd_details_str += """\
                                    Date - %s <br>
                                    From - %s <br>
                                    To - %s <br>
                                    Requested Departure Time - %s <br>
                                    Earliest and Latest Departure Time - %s  and %s <br>
                                    Latest Convenient Arrival Time - %s <br>
                                    Fare Type - %s <br>
                                    Indicative Cost - %s <br><br>
                                    """ % (detail['fd_date'], detail['fd_from'], detail['fd_to'],
                                            detail['fd_req_dep_time'], detail['fd_earliest_dep_time'], detail['fd_lastest_dep_time'],
                                            detail['fd_latest_conv_arrival_time'], detail['fd_fare_type'], detail['fd_indicative_cost'])

        for detail in HD_Details:
                hd_details_str += """\
                                    City/Town - %s <br>
                                    Area - %s <br>
                                    Date In - %s <br>
                                    Date Out - %s <br>
                                    Indicative Cost - %s <br><br>
                                    """ % (detail['hd_city_town'], detail['hd_area'], detail['hd_date_in'],
                                            detail['hd_date_out'], detail['hd_indicative_cost'])

        for detail in CD_Details:
                cd_details_str += """\
                                    Pick Up Location - %s <br>
                                    Pick Up Date - %s <br>
                                    Pick Up Time - %s <br>
                                    Drop Off Location - %s <br>
                                    Drop Off Date - %s <br>
                                    Drop Off Time - %s <br>
                                    Indicative Cost - %s <br><br>
                                    """ % (detail['cd_pickup_location'], detail['cd_pick_up_date'], detail['cd_pickup_time'],
                                            detail['cd_drop_off_location'], detail['cd_drop_off_date'],
                                            detail['cd_drop_off_time'], detail['cd_indicative_cost'])

        approve_reject_body = '<!-- No Buttons -->'

        if approve_link != '#' and reject_link != '#':
            approve_reject_body = """
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 80px; background: #2c3742;">&nbsp;</td>
                        <td  colspan="2" style="padding: 0; margin: 0; width: 500px; height: 80px; background: #2c3742; color: #fff; text-align: center;">
                            <em>
                                <a href="%s" target="_blank" style="background-color: #ff502d; color: #fff; text-decoration: none; font-size: 1.2em; width: 200px; padding: 8px 70px; margin-right: 30px; text-transform: uppercase;">
                                    <span style="color: #ffffff;">Reject</span>
                                </a>
                            </em>
                            <em>
                                <a href="%s" target="_blank" style="background-color: #009900; color: #fff; text-decoration: none; font-size: 1.2em; width: 200px; padding: 8px 70px; margin-left: 30px; text-transform: uppercase;">
                                    <span style="color: #ffffff;">Approve</span>
                                </a>
                            </em>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 80px; background: #2c3742;">&nbsp;</td>
                    </tr>
            """ % (reject_link, approve_link)

        msg_body = """\
                    <span style="width: 600px; padding: 1px; background: #d3d3d3; display: block;">
                    <table style="padding: 0; margin: 0; width:600px; font-family:Arial,Helvetica,sans-serif; font-size: 12px; letter-spacing: 1px; border-spacing: 0; background-color: #fff;" border="0">
                        <tbody>
                            <!-- description -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px; ">&nbsp;</td>
                                <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 50px;">
                                    <p style="color: #909090; font-size: 10px; text-align: center;"><em>This is an auto-generated e-mail. Please don't reply</em></p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px;">&nbsp;</td>
                            </tr>
                            <!-- description -->

                            <!-- opening -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                                <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 150px; background: #2c3742; color: #fff; text-align: justify;">
                                    <p>Hi, <br/><br/><br/>The request for travel authorisation has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                            </tr>
                            <!-- opening -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Passenger Details</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Surname</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">First Name(s)</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Job Titles</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Travellers Employee Number</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Business Unit</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Charge Cost Center or Project Code</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Travellers Mobile Number</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Frequent Flyer Number</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner tall row important -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Traveller's Email Address</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date of Form Completion</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Charge Account Number</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Division</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <!-- <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">ALL</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;"> -string placeholder(percent[s])- </span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr> -->
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Flight Details</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Specifics</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Total</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Do you require check in luggage</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Special Instructions</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Hotel Details</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Specifics</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Total</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Special Instructions</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Car Rental Details</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Specifics</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Total</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Do you Budget fastbreak number?</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->


                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Special Instructions</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Cab Charge</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Number of Vouchers Required</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Miscellaneous Expenses</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                                        <table style="border-spacing: 0;">
                                        <thead>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">Expense Item</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Approximate Cost per Day</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Number of Travellers</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Number of Days</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Indicative Cost</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Airport Parking</td>
                                                <td style="padding: 5px; text-align: center;">$35.00</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Meal Allowance - Breakfast</td>
                                                <td style="padding: 5px; text-align: center;">$30.00</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Meal Allowance - Dinner</td>
                                                <td style="padding: 5px; text-align: center;">$60.00</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td colspan="3">&nbsp;</td>
                                                <td><strong>Total</strong></td>
                                                <td><strong>%s</strong></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Requirements Prior to Departure</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                                    <table style="border-spacing: 0;">
                                        <thead>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">&nbsp;</td>
                                                <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">Type of Currency</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Number of Days Overseas</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Total Amount Required</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Currency 1</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Currency 2</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Currency 3</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">AUTHORISATION</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Purpose of Travel</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Total</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Travel Authorisation</span>
                                </td>
                                <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-weight: bold; color: #009900;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                                    <table style="border-spacing: 0; width: %s;">
                                        <thead>
                                            <tr>
                                                <td colspan=2 style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">&nbsp;</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Name</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Position</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Date</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td colspan=2 style="font-weight: bold; width: 130px; padding: 5px;">Requested/Form Completed By</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td colspan=2 style="font-weight: bold; width: 130px; padding: 5px;">Authorised By</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td colspan=2 style="font-weight: bold; width: 130px; padding: 5px;">Executive Approval</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>

                            </tr>

                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                                    <table style="border-spacing: 0; width: %s;">
                                        <thead>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">&nbsp;</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Name</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Email Address</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Phone</td>
                                                <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px; text-align: center;">Date</td>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Itinerary to be returned to</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                            <tr>
                                                <td style="font-weight: bold; width: 130px; padding: 5px;">Second nominated Itinerary to be returned to</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                                <td style="padding: 5px; text-align: center;">%s</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">COMMENTS</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

                            <!-- Buttons -->
                            %s
                            <!-- Buttons -->

                            <!-- Footer -->
                             <tr>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                                <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                                    <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                                        <a style='color: #3b9ff3;' target='_blank' href='http://%s/travel_authorisations%s'>http://%s/travel_authorisations%s</a>
                                    </p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                            </tr>
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                                <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 50px;">
                                    <p style="color: #909090; font-size: 10px; text-align: center;"><em>This is an auto-generated e-mail. Please don't reply</em></p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                            </tr>
                            <!-- Footer -->

                        </tbody>
                    </table>

                    </span>
                   """ % (status, date_time, user,
                            PD_Surname, PD_Name, PD_Job_Title, PD_EmpNumber,
                            PD_Business_Unit, PD_Charge_CCNum_ProjCode, PD_Mobile, PD_Frequent_Flyer_number,
                            PD_Email, PD_Date_Completed, PD_Charge_account_number, PD_Division,
                            fd_details_str, FD_Total, FD_Checked_Baggage, FD_Special_Instructions,
                            #hd_details_str, HD_Total, HD_Corporate_Card, HD_Special_Instructions,
                            hd_details_str, HD_Total, HD_Special_Instructions,
                            cd_details_str, CD_Total, CD_Fastbreak_Number, CD_Special_Instructions,
                            Cab_Charge_Number,
                            ME_AP_Num_of_Travellers, ME_AP_Number_of_Days, ME_AP_Indicative_Cost,
                            ME_B_Num_of_Travellers, ME_B_Number_of_Days, ME_B_Indicative_Cost,
                            ME_D_Num_of_Travellers, ME_D_Number_of_Days, ME_D_Indicative_Cost, ME_Total,
                            FC1_Type_of_Currency, FC1_Num_of_Days_Overseas, FC1_Total_Amount_Requiredy,
                            FC2_Type_of_Currency, FC2_Num_of_Days_Overseas, FC2_Total_Amount_Requiredy,
                            FC3_Type_of_Currency, FC3_Num_of_Days_Overseas, FC3_Total_Amount_Requiredy,
                            AUT_Purpose_of_Travel, AUT_Total,AUT_Travel_Authorisation,'100%',
                            AUT_ComBy_Name, AUT_ComBy_Position, AUT_ComBy_Date, AUT_AuthBy_Name,
                            AUT_AuthBy_Position, AUT_AuthBy_Date, AUT_Exec_Name, AUT_Exec_Position,
                            #AUT_Exec_Date, AUT_SMG_Name, AUT_SMG_Position, AUT_SMG_Date, AUT_Itin_Name,
                            AUT_Exec_Date, '100%', AUT_Itin_Name,
                            AUT_Itin_Email, AUT_Itin_Phone, AUT_Itin_Date, AUT_SecItin_Name,
                            AUT_SecItin_Email, AUT_SecItin_Phone, AUT_SecItin_Date, additional_comments,
                            approve_reject_body,
                            domain_path, encoded_param, domain_path, encoded_param)

        if cc is not None:
            mail.send(to, subject, msg_body, user, cc=cc)
        else:
            mail.send(to, subject, msg_body, user)

    @route
    def save_form(self):
        self.components.drafts.clear()
        to = self.request.get('to')
        cc = self.request.get('cc')
        type_of_travel = self.request.get('type_of_travel')

        #PASSENGER DETAILS
        PD_Surname = self.request.get('surname')
        PD_Name = self.request.get('first_names')
        PD_Job_Title = self.request.get('PD_Job_Title')
        PD_EmpNumber = self.request.get('PD_EmpNumber')
        PD_Business_Unit = self.request.get('PD_Business_Unit')
        PD_Charge_CCNum_ProjCode = self.request.get('PD_Charge_CCNum_ProjCode')
        PD_Mobile = self.request.get('PD_Mobile')
        PD_Frequent_Flyer_number = self.request.get('PD_Frequent_Flyer_number')
        PD_Email = self.request.get('PD_Email')
        PD_Date_Completed = self.request.get('PD_Date_Completed')
        PD_Charge_account_number = self.request.get('PD_Charge_account_number')
        PD_Division = self.request.get('PD_Division')

        # FLIGHT DETAILS
        fd_date = self.request.get_all('FD_Date[]')
        fd_from = self.request.get_all('FD_From[]')
        fd_to = self.request.get_all('FD_To[]')
        fd_req_dep_time = self.request.get_all('FD_Req_Dep_Time[]')
        fd_earliest_dep_time = self.request.get_all('FD_Earliest_Dep_Time[]')
        fd_lastest_dep_time = self.request.get_all('FD_Latest_Dep_Time[]')
        fd_latest_conv_arrival_time = self.request.get_all('FD_Latest_Convenient_Arrival_Time[]')
        fd_fare_type = self.request.get_all('FD_Fare_Type[]')
        fd_indicative_cost = self.request.get_all('FD_Indicative_Cost[]')

        FD_Checked_Baggage = self.request.get('FD_Checked_Baggage')
        FD_Special_Instructions = self.request.get('FD_Special_Instructions')
        FD_Total = self.request.get('FD_Total')

        fd_details = []

        for count in range(len(fd_date)):
            fd_data = {}

            fd_data['fd_date'] = Utils.html_escape(fd_date[count])
            fd_data['fd_from'] = Utils.html_escape(fd_from[count])
            fd_data['fd_to'] = Utils.html_escape(fd_to[count])
            fd_data['fd_req_dep_time'] = Utils.html_escape(fd_req_dep_time[count])
            fd_data['fd_earliest_dep_time'] = Utils.html_escape(fd_earliest_dep_time[count])
            fd_data['fd_lastest_dep_time'] = Utils.html_escape(fd_lastest_dep_time[count])
            fd_data['fd_latest_conv_arrival_time'] = Utils.html_escape(fd_latest_conv_arrival_time[count])
            fd_data['fd_fare_type'] = Utils.html_escape(fd_fare_type[count])
            fd_data['fd_indicative_cost'] = Utils.html_escape(fd_indicative_cost[count])

            fd_details.append(fd_data)

        FD_Details = json.dumps(fd_details)

        # HOTEL DETAILS
        hd_city_town = self.request.get_all('HD_City_Town[]')
        hd_area = self.request.get_all('HD_Area[]')
        hd_date_in = self.request.get_all('HD_Date_In[]')
        hd_date_out = self.request.get_all('HD_Date_Out[]')
        hd_indicative_cost = self.request.get_all('HD_Indicative_Cost[]')

        #HD_Corporate_Card = self.request.get('HD_Corporate_Card')
        HD_Special_Instructions = self.request.get('HD_Special_Instructions')
        HD_Total = self.request.get('HD_Total')

        hd_details = []

        for count in range(len(hd_city_town)):
            hd_data = {}

            hd_data['hd_city_town'] = Utils.html_escape(hd_city_town[count])
            hd_data['hd_area'] = Utils.html_escape(hd_area[count])
            hd_data['hd_date_in'] = Utils.html_escape(hd_date_in[count])
            hd_data['hd_date_out'] = Utils.html_escape(hd_date_out[count])
            hd_data['hd_indicative_cost'] = Utils.html_escape(hd_indicative_cost[count])

            hd_details.append(hd_data)

        HD_Details = json.dumps(hd_details)

        # CAR RENTAL DETAILS
        cd_pickup_location = self.request.get_all('CD_Pick_Up_Location[]')
        cd_pick_up_date = self.request.get_all('CD_Pick_Up_Date[]')
        cd_pickup_time = self.request.get_all('CD_Pick_Up_Time[]')
        cd_drop_off_location = self.request.get_all('CD_Drop_Off_Location[]')
        cd_drop_off_date = self.request.get_all('CD_Drop_Off_Date[]')
        cd_drop_off_time = self.request.get_all('CD_Drop_Off_Time[]')
        cd_indicative_cost = self.request.get_all('CD_Indicative_Cost[]')

        CD_Fastbreak_Number = self.request.get('CD_Fastbreak_Number')
        CD_Special_Instructions = self.request.get('CD_Special_Instructions')
        CD_Total = self.request.get('CD_Total')

        cd_details = []

        for count in range(len(cd_pickup_location)):
            cd_data = {}
            cd_data['cd_pickup_location'] = Utils.html_escape(cd_pickup_location[count])
            cd_data['cd_pick_up_date'] = Utils.html_escape(cd_pick_up_date[count])
            cd_data['cd_pickup_time'] = Utils.html_escape(cd_pickup_time[count])
            cd_data['cd_drop_off_location'] = Utils.html_escape(cd_drop_off_location[count])
            cd_data['cd_drop_off_date'] = Utils.html_escape(cd_drop_off_date[count])
            cd_data['cd_drop_off_time'] = Utils.html_escape(cd_drop_off_time[count])
            cd_data['cd_indicative_cost'] = Utils.html_escape(cd_indicative_cost[count])

            cd_details.append(cd_data)

        CD_Details = json.dumps(cd_details)

        # CAB CHARGE
        Cab_Charge_Number = self.request.get('Cab_Charge_Number')

        # MISCELLANEOUS EXPENSES
        ME_AP_Num_of_Travellers = self.request.get('ME_AP_Num_of_Travellers')
        ME_AP_Number_of_Days = self.request.get('ME_AP_Number_of_Days')
        ME_AP_Indicative_Cost = self.request.get('ME_AP_Indicative_Cost')
        ME_B_Num_of_Travellers = self.request.get('ME_B_Num_of_Travellers')
        ME_B_Number_of_Days = self.request.get('ME_B_Number_of_Days')
        ME_B_Indicative_Cost = self.request.get('ME_B_Indicative_Cost')
        ME_D_Num_of_Travellers = self.request.get('ME_D_Num_of_Travellers')
        ME_D_Number_of_Days = self.request.get('ME_D_Number_of_Days')
        ME_D_Indicative_Cost = self.request.get('ME_D_Indicative_Cost')
        ME_Total = self.request.get('ME_Total')

        #REQUIREMENTS PRIOR TO DEPARTURE
        FC1_Type_of_Currency = self.request.get('FC1_Type_of_Currency')
        FC1_Num_of_Days_Overseas = self.request.get('FC1_Num_of_Days_Overseas')
        FC1_Total_Amount_Requiredy = self.request.get('FC1_Total_Amount_Requiredy')
        FC2_Type_of_Currency = self.request.get('FC2_Type_of_Currency')
        FC2_Num_of_Days_Overseas = self.request.get('FC2_Num_of_Days_Overseas')
        FC2_Total_Amount_Requiredy = self.request.get('FC2_Total_Amount_Requiredy')
        FC3_Type_of_Currency = self.request.get('FC3_Type_of_Currency')
        FC3_Num_of_Days_Overseas = self.request.get('FC3_Num_of_Days_Overseas')
        FC3_Total_Amount_Requiredy = self.request.get('FC3_Total_Amount_Requiredy')

        #AUTHORISATION
        AUT_Purpose_of_Travel = self.request.get('AUT_Purpose_of_Travel')
        AUT_Total = self.request.get('AUT_Total')
        AUT_Travel_Authorisation = self.request.get('AUT_Travel_Authorisation')

        AUT_ComBy_Name = self.request.get('AUT_ComBy_Name')
        AUT_ComBy_Position = self.request.get('AUT_ComBy_Position')
        AUT_ComBy_Date = self.request.get('AUT_ComBy_Date')
        AUT_AuthBy_Name = self.request.get('AUT_AuthBy_Name')
        AUT_AuthBy_Position = self.request.get('AUT_AuthBy_Position')
        AUT_AuthBy_Date = self.request.get('AUT_AuthBy_Date')
        AUT_Exec_Name = self.request.get('AUT_Exec_Name')
        AUT_Exec_Position = self.request.get('AUT_Exec_Position')
        AUT_Exec_Date = self.request.get('AUT_Exec_Date')
        #AUT_SMG_Name = self.request.get('AUT_SMG_Name')
        #AUT_SMG_Position = self.request.get('AUT_SMG_Position')
        #AUT_SMG_Date = self.request.get('AUT_SMG_Date')

        AUT_Itin_Name = self.request.get('AUT_Itin_Name')
        AUT_Itin_Email = self.request.get('AUT_Itin_Email')
        AUT_Itin_Phone = self.request.get('AUT_Itin_Phone')
        AUT_Itin_Date = self.request.get('AUT_Itin_Date')
        AUT_SecItin_Name = self.request.get('AUT_SecItin_Name')
        AUT_SecItin_Email = self.request.get('AUT_SecItin_Email')
        AUT_SecItin_Phone = self.request.get('AUT_SecItin_Phone')
        AUT_SecItin_Date = self.request.get('AUT_SecItin_Date')

        # Saving...
        save = TravelAuthorisation(to=to, cc=cc, type_of_travel=type_of_travel,
                                    PD_Surname=PD_Surname, PD_Name=PD_Name, PD_EmpNumber=PD_EmpNumber, PD_Job_Title=PD_Job_Title, PD_Business_Unit=PD_Business_Unit, PD_Charge_CCNum_ProjCode=PD_Charge_CCNum_ProjCode, PD_Mobile=PD_Mobile,
                                    PD_Frequent_Flyer_number=PD_Frequent_Flyer_number, PD_Email=PD_Email, PD_Date_Completed=PD_Date_Completed, PD_Charge_account_number=PD_Charge_account_number, PD_Division=PD_Division,
                                    FD_Details=FD_Details, FD_Checked_Baggage=FD_Checked_Baggage, FD_Special_Instructions=FD_Special_Instructions, FD_Total=FD_Total,
                                    #HD_Details=HD_Details, HD_Corporate_Card=HD_Corporate_Card, HD_Special_Instructions=HD_Special_Instructions, HD_Total=HD_Total,
                                    HD_Details=HD_Details, HD_Special_Instructions=HD_Special_Instructions, HD_Total=HD_Total,
                                    CD_Details=CD_Details, CD_Fastbreak_Number=CD_Fastbreak_Number, CD_Special_Instructions=CD_Special_Instructions, CD_Total=CD_Total,
                                    Cab_Charge_Number=Cab_Charge_Number,
                                    ME_AP_Num_of_Travellers=ME_AP_Num_of_Travellers, ME_AP_Number_of_Days=ME_AP_Number_of_Days, ME_AP_Indicative_Cost=ME_AP_Indicative_Cost, ME_B_Num_of_Travellers=ME_B_Num_of_Travellers,
                                    ME_B_Number_of_Days=ME_B_Number_of_Days, ME_B_Indicative_Cost=ME_B_Indicative_Cost, ME_D_Num_of_Travellers=ME_D_Num_of_Travellers, ME_D_Number_of_Days=ME_D_Number_of_Days, ME_D_Indicative_Cost=ME_D_Indicative_Cost,
                                    ME_Total=ME_Total,
                                    FC1_Type_of_Currency=FC1_Type_of_Currency, FC1_Num_of_Days_Overseas=FC1_Num_of_Days_Overseas, FC1_Total_Amount_Requiredy=FC1_Total_Amount_Requiredy, FC2_Type_of_Currency=FC2_Type_of_Currency,
                                    FC2_Num_of_Days_Overseas=FC2_Num_of_Days_Overseas, FC2_Total_Amount_Requiredy=FC2_Total_Amount_Requiredy, FC3_Type_of_Currency=FC3_Type_of_Currency, FC3_Num_of_Days_Overseas=FC3_Num_of_Days_Overseas,
                                    FC3_Total_Amount_Requiredy=FC3_Total_Amount_Requiredy,
                                    AUT_Purpose_of_Travel=AUT_Purpose_of_Travel, AUT_Total=AUT_Total, AUT_Travel_Authorisation=AUT_Travel_Authorisation, AUT_ComBy_Name=AUT_ComBy_Name, AUT_ComBy_Position=AUT_ComBy_Position, AUT_ComBy_Date=AUT_ComBy_Date,
                                    AUT_AuthBy_Name=AUT_AuthBy_Name, AUT_AuthBy_Position=AUT_AuthBy_Position, AUT_AuthBy_Date=AUT_AuthBy_Date, AUT_Exec_Name=AUT_Exec_Name, AUT_Exec_Position=AUT_Exec_Position, AUT_Exec_Date=AUT_Exec_Date,
                                    #AUT_SMG_Name=AUT_SMG_Name, AUT_SMG_Position=AUT_SMG_Position, AUT_SMG_Date=AUT_SMG_Date, AUT_Itin_Name=AUT_Itin_Name, AUT_Itin_Email=AUT_Itin_Email, AUT_Itin_Phone=AUT_Itin_Phone, AUT_Itin_Date=AUT_Itin_Date, AUT_SecItin_Name=AUT_SecItin_Name,
                                    AUT_Itin_Name=AUT_Itin_Name, AUT_Itin_Email=AUT_Itin_Email, AUT_Itin_Phone=AUT_Itin_Phone, AUT_Itin_Date=AUT_Itin_Date, AUT_SecItin_Name=AUT_SecItin_Name,
                                    AUT_SecItin_Email=AUT_SecItin_Email, AUT_SecItin_Phone=AUT_SecItin_Phone, AUT_SecItin_Date=AUT_SecItin_Date).put()

        # Send Notification
        result = save.get()

        status = 'Sent'
        additional_comments = 'N/A'
        subject = "Travel Authorisation Request Notification"
        recipients = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
        #recipients += to
        domain_path = self.session.get('DOMAIN_PATH')

        if cc is None or str(cc) == "":
            cc = None

        form_key = self.request.get('FORM_KEY')
        logging.info("TRAVEL AUTH FORM KEY ===========> %s", form_key)
        # view_key = str(result.key.urlsafe())
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key
        key = result.key.urlsafe()

        cc_app_rej = None

        # Create approve/reject link
        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'approve')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject')

        self.sendMail(status, result, additional_comments, recipients, subject, domain_path, encoded_param, cc_app_rej, approve_link, reject_link)
        self.sendMail(status, result, additional_comments, to, subject, domain_path, encoded_param, cc)
        return 'True'
