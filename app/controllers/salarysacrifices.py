from ferris import Controller, scaffold,route
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from google.appengine.api import users
from google.appengine.ext import ndb
from ferris.core import mail
from ..controllers.utils import Utils
from ..models.salarysacrifice import Salarysacrifice
from ..controllers.users import Users
import logging
from app.component.drafts import Drafts
from plugins import directory
from google.appengine.api import app_identity
from google.appengine.ext import blobstore
import urllib2


class Salarysacrifices(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, Pagination, Upload, Drafts)
        pagination_limit = 10
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
    def generate_upload_url(self):
        url = self.session.get('unquoted_url')
        return blobstore.create_upload_url(success_path=url)

    @route
    def form(self):
        form_key = self.context.get('form_key')
        self.context['frmkey'] = form_key
        url = urllib2.unquote(self.request.url)
        self.session['unquoted_url'] = url

        def after_save(controller, container, item):
            form = item
            ui_item = self.request.params

            try:
                include_cc = ui_item['submit_response']
            except:
                include_cc = 'No'

            domainpath = controller.session.get('DOMAIN_PATH')

            encoded_param = "?key=" + form_key
            user_email = controller.session.get('user_email')

            keyid = form.key.urlsafe()
            item_data = self.util.decode_key(keyid).get()

            self.sendNotifFromUser(controller, form, user_email, item_data, include_cc, domainpath, encoded_param)

        self.events.scaffold_after_save += after_save
        self.context['user'] = self.session.get('user_email')
        for key, value in self.session.items():
            self.context[key] = value

        try:
            userinfodict = directory.get_user_by_email(self.session.get('user_email'))
        except:
            userinfodict = None

        logging.info('USER INFO DICT ====================>' + str(userinfodict))

        if userinfodict:
            self.context['user_info_fullname'] = userinfodict.get('name').get('fullName', '')
            self.context['location'] = userinfodict.get('location', '')
            self.context['division'] = userinfodict.get('division', '')
            self.context['employeeId'] = userinfodict.get('employeeId', '')
            self.context['costCentre'] = userinfodict.get('costCentre', '')
            self.context['position'] = userinfodict.get('position', '')

        self.scaffold.redirect = '/salarysacrifices?key=' + form_key
        return scaffold.add(self)

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        frmkey = self.request.params['key']
        self.context['frmkey'] = frmkey

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and Salarysacrifice.created_by or -Salarysacrifice.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and Salarysacrifice.Status or -Salarysacrifice.Status
        else:
            order = self.request.get('order_by_date') == 'desc' and Salarysacrifice.created or -Salarysacrifice.created

        if (Users.is_email_within_group(users.get_current_user().email(), self.context.get('first_group_approver').key.urlsafe())):
            logging.info('==================> USER is ' + str(users.get_current_user()))
            self.context['salarysacrifices'] = Salarysacrifice.query(Salarysacrifice.pay_cycle.IN(['Weekly', 'Fortnightly'])).order(order).fetch()

        elif (Users.is_email_within_group(users.get_current_user().email(), self.context.get('second_group_approver').key.urlsafe())):
            logging.info('==================> USER is ' + str(users.get_current_user()))
            self.context['salarysacrifices'] = Salarysacrifice.query(Salarysacrifice.pay_cycle.IN(['Monthly'])).order(order).fetch()
        else:
            self.context['salarysacrifices'] = Salarysacrifice.query(Salarysacrifice.created_by == users.get_current_user()).order(order)

        if not self.context['salarysacrifices'].fetch():

            return self.redirect(self.uri(action='form', key=frmkey))

    @route
    def cancel_app(self):

        self.context['frmkey'] = self.request.params['key']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self,key):

        item = self.util.decode_key(key).get()

        self.context['user_email'] = self.session.get('user_email')
        self.context['item'] = item
        self.context['download_link'] = Utils.generate_download_link(item.attachment)

        self.context['keyid'] = item.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotifFromUser(self, controller, form, user_email, item_data, include_cc, domainpath, encoded_param):

        question_1 = form.question_1
        question_2 = form.question_2
        question_3 = form.question_3
        question_4 = form.question_4
        question_5 = form.question_5
        question_6 = form.question_6
        question_7 = form.question_7
        question_8 = form.question_8

        full_name = form.full_name
        payroll_number = form.payroll_number
        cost_centre = form.cost_centre
        location_name = form.location_name
        device_purchase_type = form.device_purchase_type
        employment_status = form.employment_status
        pay_cycle = form.pay_cycle
        device_description = form.device_description
        purchase_amount = form.purchase_amount
        gst_amount = form.gst_amount
        purchase_date = form.purchase_date
        attachment = form.attachment

        if include_cc == 'Yes':
            cc = user_email
        else:
            cc = None

        subject = "Computing Device Salary Application - " + str(user_email)

        # Depending upon the pay cycle send the notification email to a group of approvers.
        if pay_cycle == 'Weekly' or pay_cycle == 'Fortnightly':
            send_email_to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
        else:
            send_email_to = Users.get_user_list_by_group(controller.context.get('second_group_approver').key.urlsafe())


        if  not send_email_to:
            raise Exception("No salary sacrifice employee approver email address has been configured " +
                            "for %s based employees. Please contact the administrator of this form to ensure an approver group is assigned." % pay_cycle.lower())


        # Send email notification to NPO Team Member

        if attachment is not None and attachment is not "":

            status = "Successful Application"

            item_data.Status = status
            item_data.put()

            self.sendMailOK(question_1, question_2, question_3, question_4, question_5, question_6,
            question_7, question_8, full_name, payroll_number, cost_centre, location_name, device_purchase_type,
            employment_status, pay_cycle, device_description, purchase_amount, gst_amount, purchase_date,
            attachment, status, subject, send_email_to, cc, user_email, domainpath, encoded_param)

    @classmethod
    def sendMailOK(self,question_1, question_2, question_3, question_4, question_5, question_6,
            question_7, question_8, full_name, payroll_number, cost_centre, location_name, device_purchase_type,
            employment_status, pay_cycle, device_description, purchase_amount, gst_amount, purchase_date,
            attachment, status, subject, to, cc, user_email, domainpath, encoded_param):

        attchmnt = Utils.generate_download_link(attachment)

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
                        <p>Hi, <br/><br/><br/>A new computing device salary sacrifice form has been submitted with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">1. I have read and understood the Salary Sacrifice Policy and agree to abide by the provisions which may be varied from time to time.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900; padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">2. I acknowledge that Woolworths has advised me to seek independent financial advice before considering the Woolworths offer to enter into this salary sacrifice arrangement.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">3. I understand as an eligible employee of the Woolworths Limited group I am able under the MyDevice policy to salary sacrifice up to 1 portable computing device per FBT year (1 April to 31 March).</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">4. I declare, the PRIMARY use of the device being sought for salary sacrifice will be for Woolworths Limited work/employment related purposes.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">5. I am currently entitled to or using a Woolworths provided computing device.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">6. Woolworths Limited has not already supplied me with a Laptop computer, tablet or smartphone with the same functionality as the device to which I am seeking to salary sacrifice.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">7. Any private use of the item will be incidental to the primary work use of the item.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">8. I hereby request Woolworths to deduct from my salary the amount specified below and authorize this deduction over the minimum number of pay periods required.</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;padding-left: 20px;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Purchase Details</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Full Name</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Payroll Number</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Cost Center</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Device Purchase Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employment Status</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pay Cycle</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">What you have purchased</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Purchased amount (Inclusive of GST)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">GST Amount</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Purchase Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachment Receipt</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Application Status</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- Footer -->
                 <tr>
                    <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                    <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                        <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/salarysacrifices%s'>http://%s/salarysacrifices%s</a>
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
        """ % (question_1, question_2, question_3, question_4, question_5, question_6, question_7, question_8,
            full_name, payroll_number, cost_centre, location_name, device_purchase_type, employment_status, pay_cycle,
            device_description, purchase_amount, gst_amount, purchase_date, attchmnt, status,domainpath, encoded_param, domainpath, encoded_param)

        if cc is not None:
            mail.send(to, subject, msg_body, str(user_email), cc=user_email)
        else:
            mail.send(to, subject, msg_body, str(user_email))
