from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from google.appengine.api import users
from ferris.core import mail
from ..models.poolcarbook import Poolcarbook
from ..models.woolies_form import WooliesForm
from ..controllers.utils import Utils
import logging
import urllib2
import datetime
from plugins import directory
from app.component.drafts import Drafts

class Poolcarbooks(Controller):

    class Meta:
        prefix = ('admin',)
        components = (scaffold.Scaffolding,Pagination,Drafts)
        pagination_limit = 10
        action_form = 'poolcarbookform'

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200
        
    @route
    def poolcarbookform(self):
        self.context['user_fullname'] = self.session.get('user_fullname')
        poolform = WooliesForm.query().filter(WooliesForm.list_url == 'poolcarbooks')
        
        for item in poolform:
            form_key = item.key.urlsafe()
        
        logging.info('POOL FORM KEY ==============> ' + str(form_key))
        self.context['form_key'] = form_key

        try:
            self.context['j_sdate'] = self.request.get('sdate')
            self.context['j_edate'] = self.request.get('edate')
        except:
            self.context['j_sdate'] = 'No Start date'
            self.context['j_edate'] = 'No End date'

    @route
    def add(self):

        form = self.request.params
        form_key = form['form_key']
        
        def after_save(controller, container, item):
            form = self.request.params
            user_email = self.session.get('user_email')
            domainpath = self.session.get('DOMAIN_PATH')
            to = 'norwestfm@woolworths.com.au;' + item.Authorising_Line_Manager
            #to = 'formapprover2@woolworths.com.au;' + item.Authorising_Line_Manager # For Testing Purposes

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            self.sendNotif(form,to,user_email, domainpath, encoded_param)

        self.events.scaffold_after_save += after_save

        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route
    def edit_data(self):

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

        form = self.request.params
        key = form['key']
        frmkey = form['frmkey']
        item_data = self.util.decode_key(key).get()

        item_data.Driver_Name = form['Driver_Name']
        item_data.Driver_Licence_No = form['Driver_Licence_No']
        item_data.Division_Region = form['Division_Region']
        item_data.Cost_Centre_No = form['Cost_Centre_No']
        item_data.Authorising_Line_Manager = form['Authorising_Line_Manager']
        item_data.Authorising_LM_Pos = form['Authorising_LM_Pos']
        item_data.Line_Manager_Pos = form['Line_Manager_Pos']
        item_data.End_Date_Time_Journey = form['End_Date_Time_Journey']
        item_data.Purpose_of_Journey = form['Purpose_of_Journey']
        
        item_data.put()

        return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['user_fullname'] = self.session.get('user_fullname')
        self.context['frmkey']  = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        self.context['frmkey']  = self.request.params['key']

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Poolcarbook.created_by or -Poolcarbook.created_by
        elif self.request.get('order_by_status')    :        
            order = self.request.get('order_by_status') == 'desc'  and Poolcarbook.Status or -Poolcarbook.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Poolcarbook.created or -Poolcarbook.created

        if showAll:
            self.context['poolcarbooks'] = Poolcarbook.query().order(order)
        else:
            self.context['poolcarbooks'] = Poolcarbook.query(Poolcarbook.created_by == users.get_current_user()).order(order)

    def view(self,key):

        item = self.util.decode_key(key).get()
        self.context['key'] = item.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['item'] = item

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotif(self,form,to,user_email, domain_path, encoded_param):

        domain_path = str(domain_path)

        # User Info from global address
        userinfodict = directory.get_user_by_email(user_email)

        if userinfodict:
            uname = userinfodict['fullName']
        else:
            uname = user_email

        #Subject = "Pool Car Booking Request Notifications" As requested by the client (Subject changed)
        Subject = "Pool Car Booking Notifications from " + str(uname)

        To  = to
        Driver_Name  = form['Driver_Name']
        Driver_Licence_No = form['Driver_Licence_No']
        Division_Region = form['Division_Region']
        Cost_Centre_No = form['Cost_Centre_No']
        Authorising_Line_Manager = form['Authorising_Line_Manager']
        Line_Manager_Pos = form['Line_Manager_Pos']
        Start_Date_Time_Journey = form['Start_Date_Time_Journey']
        End_Date_Time_Journey  = form['End_Date_Time_Journey']
        Purpose_of_Journey  = form['Purpose_of_Journey']
        status = 'Sent'

        self.sendMail(status,To,user_email,Subject,Driver_Name,Driver_Licence_No,Division_Region,
            Cost_Centre_No,Authorising_Line_Manager,Line_Manager_Pos,Start_Date_Time_Journey,End_Date_Time_Journey,
            Purpose_of_Journey,domain_path,encoded_param)

    @classmethod
    def sendMail(self,status,To,user_email,Subject,Driver_Name,Driver_Licence_No,Division_Region,
            Cost_Centre_No,Authorising_Line_Manager,Line_Manager_Pos,Start_Date_Time_Journey,End_Date_Time_Journey,
            Purpose_of_Journey,domain_path,encoded_param):

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
                            <p>Hi, <br/><br/><br/>The request for Pool Car Booking has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                                by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Driver's Name</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Driver's Licence No.</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Division/Region</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Cost Centre No.</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Authorising Line Manager</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Line Manager Position</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date & Time of Journey</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date & Time of Journey</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Purpose of Journey</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- Footer -->
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
        """ % (status, date_time, current_user, Driver_Name,Driver_Licence_No,Division_Region,Cost_Centre_No,Authorising_Line_Manager,
            Line_Manager_Pos, Start_Date_Time_Journey,End_Date_Time_Journey,Purpose_of_Journey)

        mail.send(To, Subject, msg_body, str(user_email))
