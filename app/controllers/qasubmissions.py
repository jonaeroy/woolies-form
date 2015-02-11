from ferris import Controller, scaffold, route, route_with
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from google.appengine.api import users
from ferris.core import mail
from ..models.qasubmission import Qasubmission
from ..controllers.utils import Utils
import logging
import urllib2
import datetime
from app.component.drafts import Drafts
from google.appengine.ext import blobstore

class Qasubmissions(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, Pagination, Upload, Drafts)
        pagination_limit = 10
        action_form = 'qasubmissionform'

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200
        
    @route
    def qasubmissionform(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = item
            uiparams = self.request.params
            dateSent = uiparams['dateSent']
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            
            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key
            action = 'new'

            Qasubmissions.sendNotifFromUser(form,user_email,domainpath,dateSent,encoded_param,action)

        self.events.scaffold_after_save += after_save
        self.context['user'] = self.session.get('user_email')
        self.scaffold.redirect = '/qasubmissions?key=' + form_key
        return scaffold.add(self)

    @route_with(template='/qasubmissions/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.QA_number)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/qasubmissions/page/edit/<key>/<form_key>')
    def edit_data(self, key, form_key):
        item = self.util.decode_key(key).get()

        if item.Attachment is not None:
            attachment = blobstore.BlobInfo.get(item.Attachment)
            attachment = attachment.filename
            self.context['attachment'] = attachment
        else:
            self.context['attachment'] = None

        self.context['item'] = item
        self.context['frmkey'] = form_key
        self.context['key'] = key

        self.meta.view.template_name = 'qasubmissions/update.html'
        self.scaffold.redirect = '/qasubmissions?key=' + form_key

        def after_save(controller, container, item):
            form = item
            uiparams = self.request.params
            dateSent = uiparams['dateSent']
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            
            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key
            action = 'edit'

            self.sendNotifFromUser(form,user_email,domainpath,dateSent,encoded_param,action)

        self.events.scaffold_after_save += after_save

        return scaffold.edit(self, key)

    @route
    def delete(self,key):
        bnld = self.util.decode_key(key).get()
        bnld.key.delete()
        frmkey = self.request.params['key']
        return self.redirect(self.uri(action='delete_suc', key=frmkey))

    @route
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        frmkey = self.request.params['key']
        self.context['frmkey']  = frmkey

         #show all queries if manager of the form
        showAll = self.context.get('    ')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Qasubmission.created_by or -Qasubmission.created_by
        elif self.request.get('order_by_status')    :        
            order = self.request.get('order_by_status') == 'desc'  and Qasubmission.Status or -Qasubmission.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Qasubmission.created or -Qasubmission.created

        result = Qasubmission.query().order(order).filter(Qasubmission.To == str(users.get_current_user().email()).lower())

        if result.get():
            self.context['qasubmissions'] = result
            self.context['is_Request_Receiver'] = True
            self.context['is_Normal_User'] = False
        else:
            self.context['is_Request_Receiver'] = False
            self.context['is_Normal_User'] = True
            self.context['qasubmissions'] = Qasubmission.query(Qasubmission.created_by == users.get_current_user()).order(order)

        if not self.context['qasubmissions'].fetch():

            return self.redirect(self.uri(action='qasubmissionform', key=frmkey))

    def view(self,key):

        qasubmission = self.util.decode_key(key).get()
        current_user = self.session.get('user_email')
        
        self.context['qasubmission'] = qasubmission
        if qasubmission.QA_number == 0:
            self.context['QA_number'] = "Pending QA Number Designation"
        else:
            self.context['QA_number'] = qasubmission.QA_number

        self.context['download_link'] = Utils.generate_download_link(qasubmission.Attachment)
        self.context['keyid'] = qasubmission.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']

        if str(current_user) == str(qasubmission.created_by):
            self.context['is_requestor'] = True
        else:
            self.context['is_requestor'] = False

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotifFromUser(self,form,user_email, domainpath,dateSent,encoded_param,action):

        To = form.To
        Product_Range_Name = form.Product_Range_Name
        Is_a_product_brief_required = form.Is_a_product_brief_required
        Vendor_Name = form.Vendor_Name
        Number_of_SKUs_to_launch = form.Number_of_SKUs_to_launch
        Trading_Division = form.Trading_Division
        Brand = form.Brand
        Country_of_sale = form.Country_of_sale
        Senior_Business_Manager = form.Senior_Business_Manager
        Business_Manager = form.Business_Manager
        Sourcing_Manager = form.Sourcing_Manager
        In_Store_Date = form.In_Store_Date
        In_DC_Date = form.In_DC_Date
        Planned_lst_Ship_Date = form.Planned_lst_Ship_Date
        Is_Vendor_Currently_Supplying_to_Woolworths = form.Is_Vendor_Currently_Supplying_to_Woolworths
        Is_FPAQ_been_issued = form.Is_FPAQ_been_issued
        Brief_description_of_range = form.Brief_description_of_range
        Product_details = form.Product_details
        Attachment = form.Attachment
        QA_number = "Pending QA Number Designation"

        if action == 'edit':
            status = 'Edited'
            subject = "Change in Request: " + Product_Range_Name + " , Into " + In_DC_Date + " , " + Business_Manager + " - QA - PRO Submission"
        else:
            status = 'Sent'
            subject = Product_Range_Name + " , Into " + In_DC_Date + " , " + Business_Manager + " - QA - PRO Submission"

        Qasubmissions.sendMailFromUser(status,dateSent, To, user_email, subject, Product_Range_Name, Is_a_product_brief_required, 
            Vendor_Name, Number_of_SKUs_to_launch, Trading_Division, Brand, Country_of_sale, Senior_Business_Manager,
            Business_Manager, Sourcing_Manager, In_Store_Date, In_DC_Date,
            Planned_lst_Ship_Date,Is_Vendor_Currently_Supplying_to_Woolworths,Is_FPAQ_been_issued,
            Brief_description_of_range,Product_details,Attachment,QA_number,domainpath,encoded_param)

    @classmethod
    def sendMailFromUser(self,status, dateSent,To, user_email,subject, Product_Range_Name, Is_a_product_brief_required, 
            Vendor_Name, Number_of_SKUs_to_launch, Trading_Division, Brand, Country_of_sale, Senior_Business_Manager,
            Business_Manager, Sourcing_Manager, In_Store_Date, In_DC_Date,
            Planned_lst_Ship_Date,Is_Vendor_Currently_Supplying_to_Woolworths,Is_FPAQ_been_issued,
            Brief_description_of_range,Product_details,Attachment,QA_number,domainpath,encoded_param):

        attchmnt = Utils.generate_download_link(Attachment)
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
                            <p>Hi, <br/><br/><br/>The request for QA PRO Submission has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Request Creator</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s on %s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">To</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Product Range Name</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Is a Product Brief Required</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Number of SKUs to Launch</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Brand</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Country of Sale</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">In Store Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">In DC Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Planned first ship date(if product being indented)</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Vendor Name</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Trading Division</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Senior Business Manager</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Business Manager</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sourcing Manager</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Is Vendor Currently Supplying to Woolworths?</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">If No, has Factory Pre Audit Questionnaire (FPAQ) been issued?</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Brief description of range (or attach document outlining range)</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 row 2 liner -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Product details, descriptions, article numbers 
                                (eg. Keycodes, referral numbers, and item numbers)</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachments</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">QA Number</span>
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
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/qasubmissions%s'>http://%s/qasubmissions%s</a>
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
        """ % (status, date_time, current_user,user_email,dateSent,To,Product_Range_Name,Is_a_product_brief_required,Number_of_SKUs_to_launch,
            Brand,Country_of_sale,In_Store_Date,In_DC_Date,Planned_lst_Ship_Date,
            Vendor_Name,Trading_Division, Senior_Business_Manager,Business_Manager,
            Sourcing_Manager,Is_Vendor_Currently_Supplying_to_Woolworths, 
            Is_FPAQ_been_issued,Brief_description_of_range,Product_details,attchmnt,QA_number,
            domainpath, encoded_param, domainpath, encoded_param)

        mail.send(To, subject, msg_body, str(user_email))

    @route
    def sendNotif(self):

        user_email = self.session.get('user_email')
        domainpath = self.session.get('DOMAIN_PATH')
        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        form = self.request.params
        To = form['to']
        qa_num = int(form['qa_num'])
        keyid = form['keyid']
        qasubmission = self.util.decode_key(keyid).get()

        if str(keyid) != "" and qasubmission is not None:
            qasubmission.QA_number = qa_num
            qasubmission.put()

            subject = "QA - PRO Submission Request: QA Number Designated"

            Qasubmissions.sendMail(To, user_email, subject,qa_num,domainpath,encoded_param)

            return self.redirect(self.uri(action='list', key=form_key))

        else:
            return "<br><br><br><center><b>This request has been Deleted by user. Back to <a href='http://" + str(domainpath) + "/qasubmissions" + str(encoded_param) + "'>list.</a></b></center>"

    @classmethod
    def sendMail(self,To, user_email,subject, qa_num,domainpath,encoded_param):

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
                            <p>Hi, <br/><br/><br/>The QA number for the request for QA PRO Submission has been <span style="color: #ff502d">Allocated</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">QA Number</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">QA Number designated by</span>
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
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/qasubmissions%s'>http://%s/qasubmissions%s</a>
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
        """ % (date_time, current_user, qa_num, user_email, domainpath, encoded_param, domainpath, encoded_param)

        mail.send(To, subject, msg_body, str(user_email))