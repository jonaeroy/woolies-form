from ferris import Controller, scaffold, route, route_with
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from google.appengine.api import users
from ferris.core import mail
from ..controllers.utils import Utils
from ..models.leaveapp import Leaveapp
from plugins import directory
import logging
import datetime
from dateutil import tz
from ferris.core.ndb import ndb
from app.component.drafts import Drafts
from app.component.split_view import SplitView

class Leaveapps(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Upload, Drafts)
        pagination_limit = 10
        sv_result_variable = 'leaveapps'
        sv_status_field = 'Status'
        action_form = 'form'

    class Scaffold:
        display_properties = ('created_by', 'created')

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

    @route
    def form(self):
        # User Info from global address
        try:
            userinfodict = directory.get_user_by_email(self.session.get('primaryEmail'))
        except:
            userinfodict = None

        logging.info('USER INFO DICT ====================>' + str(userinfodict))

        if userinfodict:

            self.context['user_info_email'] = userinfodict['email']
            self.context['user_info_fullname'] = userinfodict['fullName']

            self.context['location']   = userinfodict['location']
            self.context['division']   = userinfodict['division']
            self.context['employeeId'] = userinfodict['employeeId']
            self.context['costCentre'] = userinfodict['costCentre']
            self.context['position']   = userinfodict['position']

            #self.context['user_info_phone'] = userinfodict['phone']
            #self.context['fax'] = userinfodict['fax']

        for key, value in self.session.items():
            self.context[key] = value

    @route
    def delete(self,key):
        item = self.util.decode_key(key).get()
        item.key.delete()
        frmkey = self.request.params['key']
        return self.redirect(self.uri(action='delete_suc', key=frmkey))

    @route
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def add(self):

        form_key = self.context.get('form_key')

        def after_save(controller, container, item):
            form = item
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')
            key = item.key.urlsafe()

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'reject')

            self.sendNotifFromUser(form,user_email,domainpath,encoded_param, approve_link, reject_link, 'new')

        self.events.scaffold_after_save += after_save
        self.context['user'] = self.session.get('user_email')

        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        self.context['frmkey']  = self.request.params['key']

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Leaveapp.created_by or -Leaveapp.created_by
        elif self.request.get('order_by_status') :
            order = self.request.get('order_by_status') == 'desc'  and Leaveapp.Status or -Leaveapp.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Leaveapp.created or -Leaveapp.created

        result = Leaveapp.query().order(order).filter(Leaveapp.Line_Manager == str(users.get_current_user().email()).lower())

        if result.get():

            self.context['leaveapps'] = result
            self.context['is_Line_Manager'] = True
        else:
            self.context['is_Line_Manager'] = False
            if showAll:
                self.context['leaveapps'] = Leaveapp.query().order(order)
            else:
                query = Leaveapp.query(Leaveapp.created_by == users.get_current_user()).order(order)
                self.context['leaveapps'] = query

        self.context['sv_leaveapps'] = self.context['leaveapps']

    def view(self,key):

        item = self.util.decode_key(key).get()
        current_user = self.session.get('user_email')

        self.context['key'] = item.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['item'] = item

        payroll_office = item.Payroll_Office.rsplit(':',1)[-1]

        self.context['payroll_office'] = payroll_office

        statusVar = item.Status
        self.context['status'] = Utils.convertStatus(statusVar)

        if str(current_user) == str(item.created_by):
            self.context['is_requestor'] = True
        else:
            self.context['is_requestor'] = False

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def edit_data(self):

        form = self.request.params
        key = form['key']
        frmkey = form['frmkey']
        item = self.util.decode_key(key).get()

        item.Line_Manager = form['Line_Manager']
        item.HR_Managers = form['HR_Managers']

        item.Payroll_Office = form['Payroll_Office']
        item.Location_Name = form['Location_Name']
        item.Region_Division = form['Region_Division']
        item.Employee_ID_Number = form['Employee_ID_Number']
        item.Position = form['Position']
        item.Location_Cost_Center = form['Location_Cost_Center']
        item.Employee_Type = form['Employee_Type']
        item.Pay_Frequency = form['Pay_Frequency']

        item.LD_TOL_Grp1 = form['LD_TOL_Grp1']
        item.LD_First_Working_DOL1 = form['LD_First_Working_DOL1']
        item.LD_Last_Working_DOL1 = form['LD_Last_Working_DOL1']
        item.LD_Total_Number_WH1 = form['LD_Total_Number_WH1']
        item.LD_Date_RTW1 = form['LD_Date_RTW1']

        item.LD_TOL_Grp2 = form['LD_TOL_Grp2']
        item.LD_First_Working_DOL2 = form['LD_First_Working_DOL2']
        item.LD_Last_Working_DOL2 = form['LD_Last_Working_DOL2']
        item.LD_Total_Number_WH2 = form['LD_Total_Number_WH2']
        item.LD_Date_RTW2 = form['LD_Date_RTW2']

        item.LD_TOL_Grp3 = form['LD_TOL_Grp3']
        item.LD_First_Working_DOL3 = form['LD_First_Working_DOL3']
        item.LD_Last_Working_DOL3 = form['LD_Last_Working_DOL3']
        item.LD_Total_Number_WH3 = form['LD_Total_Number_WH3']
        item.LD_Date_RTW3 = form['LD_Date_RTW3']

        item.LD_TOL_Grp4 = form['LD_TOL_Grp4']
        item.LD_First_Working_DOL4 = form['LD_First_Working_DOL4']
        item.LD_Last_Working_DOL4 = form['LD_Last_Working_DOL4']
        item.LD_Total_Number_WH4 = form['LD_Total_Number_WH4']
        item.LD_Date_RTW4 = form['LD_Date_RTW4']

        item.Full_Time_Question = form['Full_Time_Question']

        item.Annual_Leave_Only_Hours1 = form['Annual_Leave_Only_Hours1']
        item.Annual_Leave_Percentage1 = form['Annual_Leave_Percentage1']
        item.Annual_Leave_Only_Hours2 = form['Annual_Leave_Only_Hours2']
        item.Annual_Leave_Percentage2 = form['Annual_Leave_Percentage2']
        item.Annual_Leave_Only_Hours3 = form['Annual_Leave_Only_Hours3']
        item.Annual_Leave_Percentage3 = form['Annual_Leave_Percentage3']
        item.Annual_Leave_Only_Hours4 = form['Annual_Leave_Only_Hours4']
        item.Annual_Leave_Percentage4 = form['Annual_Leave_Percentage4']

        item.Public_Holiday_Dates1 = form['Public_Holiday_Dates1']
        item.Public_Holiday_Hours1 = form['Public_Holiday_Hours1']
        item.Public_Holidays_Percentage1 = form['Public_Holidays_Percentage1']

        item.Public_Holiday_Dates2 = form['Public_Holiday_Dates2']
        item.Public_Holiday_Hours2 = form['Public_Holiday_Hours2']
        item.Public_Holidays_Percentage2 = form['Public_Holidays_Percentage2']

        item.Public_Holiday_Dates3 = form['Public_Holiday_Dates3']
        item.Public_Holiday_Hours3 = form['Public_Holiday_Hours3']
        item.Public_Holidays_Percentage3 = form['Public_Holidays_Percentage3']

        item.Public_Holiday_Dates1 = form['Public_Holiday_Dates4']
        item.Public_Holiday_Hours4 = form['Public_Holiday_Hours4']
        item.Public_Holidays_Percentage4 = form['Public_Holidays_Percentage4']

        item.RD_On_Mon = form['RD_On_Mon']
        item.RD_On_Tues = form['RD_On_Tues']
        item.RD_On_Wed = form['RD_On_Wed']
        item.RD_On_Thurs = form['RD_On_Thurs']
        item.RD_On_Fri = form['RD_On_Fri']
        item.RD_On_Sat = form['RD_On_Sat']
        item.RD_On_Sun = form['RD_On_Sun']
        item.RD_On_Total = form['RD_On_Total']

        item.RD_Off_Mon = form['RD_Off_Mon']
        item.RD_Off_Tues = form['RD_Off_Tues']
        item.RD_Off_Wed = form['RD_Off_Wed']
        item.RD_Off_Thurs = form['RD_Off_Thurs']
        item.RD_Off_Fri = form['RD_Off_Fri']
        item.RD_Off_Sat = form['RD_Off_Sat']
        item.RD_Off_Sun = form['RD_Off_Sun']
        item.RD_Off_Total = form['RD_Off_Total']

        item.Status = int(form['Status'])
        item.put()

        user_email = self.session.get('user_email')
        domainpath = self.session.get('DOMAIN_PATH')
        form_key = frmkey
        encoded_param = "?key=" + form_key

        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'approve')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'reject')

        self.sendNotifFromUser(item,user_email, domainpath, encoded_param, approve_link, reject_link,'edit')
        return self.redirect(self.uri(action='list', key=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route_with(template='/leaveapps/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.Status)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @classmethod
    def sendNotifFromUser(self,form,user_email, domainpath, encoded_param, approve_link, reject_link, action):

        if action == 'edit':
            status = 'Edited'
            subject = 'Change in Leave Application Request Notification'
        else:
            status = 'Sent'
            subject = 'Leave Application Request Notification'

        # Send email notification to Merchandise Manager

        self.sendMailFromUser(form, status, subject, user_email, domainpath,encoded_param, approve_link, reject_link)

    @classmethod
    def sendMailFromUser(self, form, status, subject, user_email, domain_path, encoded_param, approve_link, reject_link):

        Line_Manager = form.Line_Manager
        HR_Managers = form.HR_Managers

        Payroll_Office = str(form.Payroll_Office)
        Payroll_Office = Payroll_Office.rsplit(':',1)[0]

        if HR_Managers is None or str(HR_Managers) == '':
            HR_Managers = "None"

        Location_Name = form.Location_Name
        Region_Division = form.Region_Division
        Employee_ID_Number = form.Employee_ID_Number
        Position = form.Position
        Location_Cost_Center = form.Location_Cost_Center
        Employee_Type = form.Employee_Type
        Pay_Frequency = form.Pay_Frequency

        LD_TOL_Grp1 = form.LD_TOL_Grp1
        LD_First_Working_DOL1 = form.LD_First_Working_DOL1
        LD_Last_Working_DOL1 = form.LD_Last_Working_DOL1
        LD_Total_Number_WH1 = form.LD_Total_Number_WH1
        LD_Date_RTW1 = form.LD_Date_RTW1

        LD_TOL_Grp2 = form.LD_TOL_Grp2
        LD_First_Working_DOL2 = form.LD_First_Working_DOL2
        LD_Last_Working_DOL2 = form.LD_Last_Working_DOL2
        LD_Total_Number_WH2 = form.LD_Total_Number_WH2
        LD_Date_RTW2 = form.LD_Date_RTW2

        LD_TOL_Grp3 = form.LD_TOL_Grp3
        LD_First_Working_DOL3 = form.LD_First_Working_DOL3
        LD_Last_Working_DOL3 = form.LD_Last_Working_DOL3
        LD_Total_Number_WH3 = form.LD_Total_Number_WH3
        LD_Date_RTW3 = form.LD_Date_RTW3

        LD_TOL_Grp4 = form.LD_TOL_Grp4
        LD_First_Working_DOL4 = form.LD_First_Working_DOL4
        LD_Last_Working_DOL4 = form.LD_Last_Working_DOL4
        LD_Total_Number_WH4 = form.LD_Total_Number_WH4
        LD_Date_RTW4 = form.LD_Date_RTW4

        Full_Time_Question = form.Full_Time_Question

        Annual_Leave_Only_Hours1 = form.Annual_Leave_Only_Hours1
        Annual_Leave_Percentage1 = form.Annual_Leave_Percentage1

        Annual_Leave_Only_Hours2 = form.Annual_Leave_Only_Hours2
        Annual_Leave_Percentage2 = form.Annual_Leave_Percentage2

        Annual_Leave_Only_Hours3 = form.Annual_Leave_Only_Hours3
        Annual_Leave_Percentage3 = form.Annual_Leave_Percentage3

        Annual_Leave_Only_Hours4 = form.Annual_Leave_Only_Hours4
        Annual_Leave_Percentage4 = form.Annual_Leave_Percentage4

        Public_Holiday_Dates1 = form.Public_Holiday_Dates1
        Public_Holiday_Hours1 = form.Public_Holiday_Hours1
        Public_Holidays_Percentage1 = form.Public_Holidays_Percentage1

        Public_Holiday_Dates2 = form.Public_Holiday_Dates2
        Public_Holiday_Hours2 = form.Public_Holiday_Hours2
        Public_Holidays_Percentage2 = form.Public_Holidays_Percentage2

        Public_Holiday_Dates3 = form.Public_Holiday_Dates3
        Public_Holiday_Hours3 = form.Public_Holiday_Hours3
        Public_Holidays_Percentage3 = form.Public_Holidays_Percentage3

        Public_Holiday_Dates4 = form.Public_Holiday_Dates4
        Public_Holiday_Hours4 = form.Public_Holiday_Hours4
        Public_Holidays_Percentage4 = form.Public_Holidays_Percentage4

        RD_On_Mon = form.RD_On_Mon
        RD_On_Tues = form.RD_On_Tues
        RD_On_Wed = form.RD_On_Wed
        RD_On_Thurs = form.RD_On_Thurs
        RD_On_Fri = form.RD_On_Fri
        RD_On_Sat = form.RD_On_Sat
        RD_On_Sun = form.RD_On_Sun
        RD_On_Total = form.RD_On_Total

        RD_Off_Mon = form.RD_Off_Mon
        RD_Off_Tues = form.RD_Off_Tues
        RD_Off_Wed = form.RD_Off_Wed
        RD_Off_Thurs = form.RD_Off_Thurs
        RD_Off_Fri = form.RD_Off_Fri
        RD_Off_Sat = form.RD_Off_Sat
        RD_Off_Sun = form.RD_Off_Sun
        RD_Off_Total = form.RD_Off_Total

        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

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
                <p>Hi, <br/><br/><br/>The request for leave application has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span>
                by %s with the following details:</p>
            </td>
            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
        </tr>
        <!-- opening -->

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">LEAVE DETAILS</span>
            </td>
            <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner 2 columns -->

        <!-- 1 liner tall row important -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Line Manager</span><br/>
                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner tall row important -->

        <!-- 1 liner tall row important -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">HR Manager</span><br/>
                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner tall row important -->

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Payroll Office</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Location Name</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Region/Division</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employee ID Number</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Position</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Location No. or Cost Centre</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employee Type</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pay Frequency</span>
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
                    <table style="border-spacing: 0;">
                    <thead>
                        <tr>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Type of Leave</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">First Working Date of Leave</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Last Working Date of Leave</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Total No. of Working Days</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Date Returning to Work</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
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

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">ROSTER DETAILS</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">For full time employees, does the employee work a 20 day month?</span>
            </td>
            <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                <span style="font-weight: bold; color: #009900;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner 2 columns -->

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="1" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                        <tr>
                            <td rowspan="5" style="color: #7d7d7d; font-weight: bold; width: 200px; padding: 5px;">Loading<br/>Annual Leave Only</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Hours</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">&#37;</td>
                        </tr>

                        <tr>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                        </tr>
                </table>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="1" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                        <tr>
                            <td rowspan="5" style="color: #7d7d7d; font-weight: bold; width: 200px; padding: 5px;">Public Holiday</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Date</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Hours</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">&#37;</td>
                        </tr>

                        <tr>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                        </tr>
                </table>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                    <thead>
                        <tr>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">&nbsp;</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Mon</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Tues</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Wed</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Thurs</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Fri</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Sat</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Sun</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Total</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">Hours on Week</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">Hours off Week<br><sub>where applicable</sub></td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
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

        <!-- Buttons -->
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
        <!-- Buttons -->

        <!-- Footer -->
         <tr>
            <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
            <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                    <a style='color: #3b9ff3;' target='_blank' href='http://%s/leaveapps%s'>http://%s/leaveapps%s</a>
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
        """ % (status, date_time, current_user, Line_Manager,HR_Managers,Payroll_Office,Location_Name,Region_Division,
            Employee_ID_Number,Position,Location_Cost_Center,Employee_Type, Pay_Frequency,
            LD_TOL_Grp1, LD_First_Working_DOL1, LD_Last_Working_DOL1, LD_Total_Number_WH1, LD_Date_RTW1,
            LD_TOL_Grp2, LD_First_Working_DOL2, LD_Last_Working_DOL2, LD_Total_Number_WH2, LD_Date_RTW2,
            LD_TOL_Grp3, LD_First_Working_DOL3, LD_Last_Working_DOL3, LD_Total_Number_WH3, LD_Date_RTW3,
            LD_TOL_Grp4, LD_First_Working_DOL4, LD_Last_Working_DOL4, LD_Total_Number_WH4, LD_Date_RTW4,
            Full_Time_Question, Annual_Leave_Only_Hours1, Annual_Leave_Only_Hours2, Annual_Leave_Only_Hours3, Annual_Leave_Only_Hours4,
            Annual_Leave_Percentage1, Annual_Leave_Percentage2, Annual_Leave_Percentage3, Annual_Leave_Percentage4,
            Public_Holiday_Dates1, Public_Holiday_Dates2, Public_Holiday_Dates3, Public_Holiday_Dates4,
            Public_Holiday_Hours1, Public_Holiday_Hours2, Public_Holiday_Hours3, Public_Holiday_Hours4,
            Public_Holidays_Percentage1, Public_Holidays_Percentage2, Public_Holidays_Percentage3, Public_Holidays_Percentage4,
            RD_On_Mon, RD_On_Tues, RD_On_Wed, RD_On_Thurs, RD_On_Fri, RD_On_Sat, RD_On_Sun, RD_On_Total,
            RD_Off_Mon, RD_Off_Tues, RD_Off_Wed, RD_Off_Thurs, RD_Off_Fri, RD_Off_Sat, RD_Off_Sun, RD_Off_Total,
            reject_link, approve_link, domain_path,encoded_param, domain_path, encoded_param)

        mail.send(Line_Manager, subject, msg_body, str(user_email))

    @route_with(template='/leaveapps/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        item = self.util.decode_key(entity_key).get()
        domain_path = self.session.get('DOMAIN_PATH')
        encoded_param = "?key=" + form_key

        if entity and item:
            approver = item.Line_Manager
            hr_managers = item.HR_Managers
            payroll_office = item.Payroll_Office
        else:
            return 404

        if approver is not None and user == str(approver) and item.Status < 2:

            if flag == 'approve':
                approval = 3
                status = "Approved"
                subject = 'Leave Application Form Approval Notification'

            elif flag == 'reject':
                approval = 4
                status = "Rejected"
                subject = 'Leave Application Form Rejection Notification'

            item.Status = approval
            item.put()

            # Send Email
            if flag == 'approve' or flag == 'reject':

                if hr_managers is not None or hr_managers is not "":
                    to = str(item.created_by) + ';' + str(hr_managers) + ';' + payroll_office
                else:
                    to = str(item.created_by) + ';' + payroll_office

                self.sendMail(item, user, status, to,subject, domain_path,encoded_param)

            # Redirect
            return self.redirect(self.uri(action='list', key=form_key, status=approval))

        if item.Status > 2:
            return "<br><br><br><center><b>This request has been Approved or Rejected. Back to <a href='http://" + str(domain_path) + "/leaveapps" + str(encoded_param) + "&status=all'>list.</a></b></center>"

        else:
            return "<br><br><br><center><b>Approver is no longer assigned to this request being approved or rejected. Back to <a href='http://" + str(domain_path) + "/leaveapps" + str(encoded_param) + "&status=all'>list.</a></b></center>"


    @route
    def sendNotif(self):

        form = self.request.params
        keyid = form['keyid']
        user_email = self.session.get('user_email')
        item = self.util.decode_key(keyid).get()

        action = str(form['action'])
        hr_managers = item.HR_Managers
        payroll_office = str(item.Payroll_Office)
        payroll_office = payroll_office.rsplit(':',1)[0]

        logging.info('PAYROLL OFFICE ===============>' + str(payroll_office))

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        if (action == "approve"):

            if hr_managers is not None or hr_managers is not "":
                to = str(item.created_by) + ';' + str(hr_managers) + ';' + payroll_office
            else:
                to = str(item.created_by) + ';' + payroll_office

            stat = 3
            item.Status = stat
            item.put()
            status = "Approved"
            subject = "Leave Application Form Approval Notification"
            self.sendMail(item,user_email,status,to,subject, self.session.get('DOMAIN_PATH'),encoded_param)

        elif (action == "reject"):

            to = str(item.created_by)
            stat = 4
            item.Status = stat
            item.put()
            status = "Rejected"
            subject = "Leave Application Form Rejection Notification"
            self.sendMail(item,user_email,status,to,subject, self.session.get('DOMAIN_PATH'),encoded_param)

        return self.redirect(self.uri(action='list', key=form_key, status=stat))

    @classmethod
    def sendMail(self,item,user_email,status,to,subject, domain_path,encoded_param):

        Line_Manager = item.Line_Manager
        HR_Managers = item.HR_Managers
        Payroll_Office = item.Payroll_Office

        if HR_Managers is None or str(HR_Managers) == '':
            HR_Managers = "None"

        Location_Name = item.Location_Name
        Region_Division = item.Region_Division
        Employee_ID_Number = item.Employee_ID_Number
        Position = item.Position
        Location_Cost_Center = item.Location_Cost_Center
        Employee_Type = item.Employee_Type
        Pay_Frequency = item.Pay_Frequency

        LD_TOL_Grp1 = item.LD_TOL_Grp1
        LD_First_Working_DOL1 = item.LD_First_Working_DOL1
        LD_Last_Working_DOL1 = item.LD_Last_Working_DOL1
        LD_Total_Number_WH1 = item.LD_Total_Number_WH1
        LD_Date_RTW1 = item.LD_Date_RTW1

        LD_TOL_Grp2 = item.LD_TOL_Grp2
        LD_First_Working_DOL2 = item.LD_First_Working_DOL2
        LD_Last_Working_DOL2 = item.LD_Last_Working_DOL2
        LD_Total_Number_WH2 = item.LD_Total_Number_WH2
        LD_Date_RTW2 = item.LD_Date_RTW2

        LD_TOL_Grp3 = item.LD_TOL_Grp3
        LD_First_Working_DOL3 = item.LD_First_Working_DOL3
        LD_Last_Working_DOL3 = item.LD_Last_Working_DOL3
        LD_Total_Number_WH3 = item.LD_Total_Number_WH3
        LD_Date_RTW3 = item.LD_Date_RTW3

        LD_TOL_Grp4 = item.LD_TOL_Grp4
        LD_First_Working_DOL4 = item.LD_First_Working_DOL4
        LD_Last_Working_DOL4 = item.LD_Last_Working_DOL4
        LD_Total_Number_WH4 = item.LD_Total_Number_WH4
        LD_Date_RTW4 = item.LD_Date_RTW4

        Full_Time_Question = item.Full_Time_Question

        Annual_Leave_Only_Hours1 = item.Annual_Leave_Only_Hours1
        Annual_Leave_Percentage1 = item.Annual_Leave_Percentage1

        Annual_Leave_Only_Hours2 = item.Annual_Leave_Only_Hours2
        Annual_Leave_Percentage2 = item.Annual_Leave_Percentage2

        Annual_Leave_Only_Hours3 = item.Annual_Leave_Only_Hours3
        Annual_Leave_Percentage3 = item.Annual_Leave_Percentage3

        Annual_Leave_Only_Hours4 = item.Annual_Leave_Only_Hours4
        Annual_Leave_Percentage4 = item.Annual_Leave_Percentage4

        Public_Holiday_Dates1 = item.Public_Holiday_Dates1
        Public_Holiday_Hours1 = item.Public_Holiday_Hours1
        Public_Holidays_Percentage1 = item.Public_Holidays_Percentage1

        Public_Holiday_Dates2 = item.Public_Holiday_Dates2
        Public_Holiday_Hours2 = item.Public_Holiday_Hours2
        Public_Holidays_Percentage2 = item.Public_Holidays_Percentage2

        Public_Holiday_Dates3 = item.Public_Holiday_Dates3
        Public_Holiday_Hours3 = item.Public_Holiday_Hours3
        Public_Holidays_Percentage3 = item.Public_Holidays_Percentage3

        Public_Holiday_Dates4 = item.Public_Holiday_Dates4
        Public_Holiday_Hours4 = item.Public_Holiday_Hours4
        Public_Holidays_Percentage4 = item.Public_Holidays_Percentage4

        RD_On_Mon = item.RD_On_Mon
        RD_On_Tues = item.RD_On_Tues
        RD_On_Wed = item.RD_On_Wed
        RD_On_Thurs = item.RD_On_Thurs
        RD_On_Fri = item.RD_On_Fri
        RD_On_Sat = item.RD_On_Sat
        RD_On_Sun = item.RD_On_Sun
        RD_On_Total = item.RD_On_Total

        RD_Off_Mon = item.RD_Off_Mon
        RD_Off_Tues = item.RD_Off_Tues
        RD_Off_Wed = item.RD_Off_Wed
        RD_Off_Thurs = item.RD_Off_Thurs
        RD_Off_Fri = item.RD_Off_Fri
        RD_Off_Sat = item.RD_Off_Sat
        RD_Off_Sun = item.RD_Off_Sun
        RD_Off_Total = item.RD_Off_Total

        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

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
                <p>Hi, <br/><br/><br/>The request for Leave application has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span>
                by %s with the following details:</p>
            </td>
            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
        </tr>
        <!-- opening -->

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">LEAVE DETAILS</span>
            </td>
            <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner 2 columns -->

        <!-- 1 liner tall row important -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Line Manager</span><br/>
                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner tall row important -->

        <!-- 1 liner tall row important -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">HR Manager</span><br/>
                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner tall row important -->

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Payroll Office</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Location Name</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Region/Division</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employee ID Number</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Position</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Location No. or Cost Centre</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employee Type</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pay Frequency</span>
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
                    <table style="border-spacing: 0;">
                    <thead>
                        <tr>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Type of Leave</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">First Working Date of Leave</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Last Working Date of Leave</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Total No. of Working Days</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Date Returning to Work</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">%s</td>
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

        <!-- 1 liner 2 columns -->
        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">ROSTER DETAILS</span>
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
                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">For full time employees, does the employee work a 20 day month?</span>
            </td>
            <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                <span style="font-weight: bold; color: #009900;">%s</span>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>
        <!-- 1 liner 2 columns -->

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="1" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                        <tr>
                            <td rowspan="5" style="color: #7d7d7d; font-weight: bold; width: 200px; padding: 5px;">Loading<br/>Annual Leave Only</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Hours</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">&#37;</td>
                        </tr>

                        <tr>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                        </tr>
                </table>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="1" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                        <tr>
                            <td rowspan="5" style="color: #7d7d7d; font-weight: bold; width: 200px; padding: 5px;">Public Holiday</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Date</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">Hours</td>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;text-align: center;">&#37;</td>
                        </tr>

                        <tr>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                            <td style="padding: 5px; text-align: center;">
                                %s<br>
                                %s<br>
                                %s<br>
                                %s<br>
                            </td>
                        </tr>
                </table>
            </td>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
        </tr>

        <tr>
            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
            <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                    <table style="border-spacing: 0;">
                    <thead>
                        <tr>
                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">&nbsp;</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Mon</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Tues</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Wed</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Thurs</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Fri</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Sat</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Sun</td>
                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Total</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">Hours on Week</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; width: 130px; padding: 5px;">Hours off Week<br><sub>where applicable</sub></td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
                            <td style="padding: 5px; text-align: center;">%s</td>
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

        <!-- Footer -->
         <tr>
            <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
            <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                    <a style='color: #3b9ff3;' target='_blank' href='http://%s/leaveapps%s'>http://%s/leaveapps%s</a>
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
        """ % (status, date_time,current_user, Line_Manager,HR_Managers,Payroll_Office,Location_Name,Region_Division,
            Employee_ID_Number,Position,Location_Cost_Center,Employee_Type, Pay_Frequency,
            LD_TOL_Grp1, LD_First_Working_DOL1, LD_Last_Working_DOL1, LD_Total_Number_WH1, LD_Date_RTW1,
            LD_TOL_Grp2, LD_First_Working_DOL2, LD_Last_Working_DOL2, LD_Total_Number_WH2, LD_Date_RTW2,
            LD_TOL_Grp3, LD_First_Working_DOL3, LD_Last_Working_DOL3, LD_Total_Number_WH3, LD_Date_RTW3,
            LD_TOL_Grp4, LD_First_Working_DOL4, LD_Last_Working_DOL4, LD_Total_Number_WH4, LD_Date_RTW4,
            Full_Time_Question, Annual_Leave_Only_Hours1, Annual_Leave_Only_Hours2, Annual_Leave_Only_Hours3, Annual_Leave_Only_Hours4,
            Annual_Leave_Percentage1, Annual_Leave_Percentage2, Annual_Leave_Percentage3, Annual_Leave_Percentage4,
            Public_Holiday_Dates1, Public_Holiday_Dates2, Public_Holiday_Dates3, Public_Holiday_Dates4,
            Public_Holiday_Hours1, Public_Holiday_Hours2, Public_Holiday_Hours3, Public_Holiday_Hours4,
            Public_Holidays_Percentage1, Public_Holidays_Percentage2, Public_Holidays_Percentage3, Public_Holidays_Percentage4,
            RD_On_Mon, RD_On_Tues, RD_On_Wed, RD_On_Thurs, RD_On_Fri, RD_On_Sat, RD_On_Sun, RD_On_Total,
            RD_Off_Mon, RD_Off_Tues, RD_Off_Wed, RD_Off_Thurs, RD_Off_Fri, RD_Off_Sat, RD_Off_Sun, RD_Off_Total,
            domain_path,encoded_param,domain_path,encoded_param)

        mail.send(to, subject, msg_body, str(user_email))
