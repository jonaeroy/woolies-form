from ferris import Controller, scaffold, route, route_with
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from google.appengine.api import users
from ..controllers.users import Users
from ferris.core import mail
from ..controllers.utils import Utils
from ..models.replenishment import Replenishment
from ferris.core.ndb import ndb
import logging
import urllib2
import datetime
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from google.appengine.ext import blobstore

class Replenishments(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Upload, Drafts)
        pagination_limit = 10
        sv_result_variable = 'replenishments'
        sv_status_field = 'Approved'
        action_form = 'replenishmentform'

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
    def delete(self,key):
        bnld = self.util.decode_key(key).get()
        bnld.key.delete()
        frmkey = self.request.params['key']
        return self.redirect(self.uri(action='delete_suc', key=frmkey))

    @route
    def replenishmentform(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = item
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key
            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'Yes')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'No')
            action = 'new'

            Replenishments.sendNotifFromUser(form,user_email,domainpath,encoded_param,approve_link,reject_link, action)

        self.events.scaffold_after_save += after_save
        
        tokey = self.context.get('first_group_approver').key.urlsafe()
        self.context['approver_details']  = Users.get_user_list_by_group(tokey)

        self.context['user'] = self.session.get('user_email')
        self.scaffold.redirect = '/replenishments?key=' + form_key
        return scaffold.add(self)

    @route
    def replenishmentapprovalform(self,key):
        selectedItem = self.util.decode_key(key).get()
        self.context['selectedItem'] = selectedItem

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route_with(template='/replenishments/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.Approved)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/replenishments/page/edit/<key>/<form_key>')
    def edit_data(self, key, form_key):
        item = self.util.decode_key(key).get()

        if item.Attachment is not None:
            attachment = blobstore.BlobInfo.get(item.Attachment)
            attachment = attachment.filename
            self.context['attachment'] = attachment
        else:
            self.context['attachment'] = None

        self.context['item'] = item
        self.context['chkboxes'] = str(item.Change_Type_cbox)
        self.context['frmkey'] = form_key
        self.context['key'] = key
        

        list_cbox = item.Change_Type_cbox.split(',')
        try:
            self.context['cbox0'] = str(list_cbox[0]).replace(' ','')
        except:
            self.context['cbox0'] = None
        try:
            self.context['cbox1'] = str(list_cbox[1]).replace(' ','')
        except:
            self.context['cbox1'] = None

        try:
            self.context['cbox2'] = str(list_cbox[2]).replace(' ','')
        except:
            self.context['cbox2'] = None

        try:
            self.context['cbox3'] = str(list_cbox[3]).replace(' ','')
        except:
            self.context['cbox3'] = None

        try:
            self.context['cbox4'] = str(list_cbox[4]).replace(' ','')
        except:
            self.context['cbox4'] = None

        self.meta.view.template_name = 'replenishments/update.html'
        self.scaffold.redirect = '/replenishments?key=' + form_key

        def after_save(controller, container, item):
            form = item
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')
            action = 'edit'

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'Yes')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'No')

            self.sendNotifFromUser(form,user_email,domainpath,encoded_param,approve_link,reject_link,action)

        self.events.scaffold_after_save += after_save

        return scaffold.edit(self, key)

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        self.context['frmkey']  = self.request.params['key']

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Replenishment.created_by or -Replenishment.created_by
        elif self.request.get('order_by_status')    :        
            order = self.request.get('order_by_status') == 'desc'  and Replenishment.Approved or -Replenishment.Approved
        else:
            order = self.request.get('order_by_date') == 'desc'  and Replenishment.created or -Replenishment.created

        tokey = self.context.get('first_group_approver').key.urlsafe()
        list_of_approvers  = Users.get_user_list_by_group(tokey).split("; ")
        current_user_email = str(users.get_current_user().email()).lower()
        is_approver        = False
        
        for approver_email in list_of_approvers:
            if  approver_email == current_user_email:
                is_approver = True
                break
            
        if  is_approver:
            self.context['replenishments'] = Replenishment.query().order(order)
            self.context['is_Approver'] = True
        else:
            self.context['is_Approver'] = False
            self.context['replenishments'] = Replenishment.query(Replenishment.created_by == users.get_current_user()).order(order)

    def view(self,key):

        dataselected = self.util.decode_key(key).get()
        current_user = self.session.get('user_email')

        self.context['dataselected'] = dataselected
        self.context['approved'] = dataselected.Approved
        self.context['download_link'] = Utils.generate_download_link(dataselected.Attachment)

        self.context['keyid'] = dataselected.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']

        if str(current_user) == str(dataselected.created_by):
            self.context['is_requestor'] = True
        else:
            self.context['is_requestor'] = False

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotifFromUser(self,form,user_email, domainpath,encoded_param,approve_link,reject_link,action):


        Requested_By = form.Requested_By
        DateAndTime = form.DateAndTime
        Approver_Details = form.Approver_Details
        Copy_to = form.Copy_to
        Implementer_Details = form.Implementer_Details
        Change_Type_ddown = form.Change_Type_ddown
        Change_Type_Detail = form.Change_Type_Detail
        Risk = form.Risk
        Priority = form.Priority
        Back_out_plan = form.Back_out_plan
        Back_out_plan_details = form.Back_out_plan_details
        Change_Type_cbox = form.Change_Type_cbox
        Implementation_date = form.Implementation_date
        End_date = form.End_date
        Attachment = form.Attachment
        ReqComments = form.ReqComments

        if action == 'edit':
            status = 'Edited'
            subject = "Change in Replenishment Change Request - " + Change_Type_ddown + " - " + DateAndTime
        else:
            status = 'Sent'
            subject = "Replenishment Change Request - " + Change_Type_ddown + " - " + DateAndTime

        # Send email notification to Approver
        self.sendMailFromUser(Requested_By, DateAndTime, Approver_Details, 
            Copy_to, Implementer_Details, Change_Type_ddown, Change_Type_Detail, 
            Risk, Priority, Back_out_plan, Back_out_plan_details, Change_Type_cbox, 
            Implementation_date, End_date, Attachment, ReqComments, status, subject, 
            user_email, domainpath,encoded_param,approve_link,reject_link)

    @classmethod
    def sendMailFromUser(self, Requested_By, DateAndTime, Approver_Details, 
            Copy_to, Implementer_Details, Change_Type_ddown, Change_Type_Detail, 
            Risk, Priority, Back_out_plan, Back_out_plan_details, Change_Type_cbox, 
            Implementation_date, End_date, Attachment,ReqComments, status, subject, 
            user_email, domainpath,encoded_param,approve_link,reject_link):

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
                        <p>Hi, <br/><br/><br/>The request for Replenishment Change has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requested By</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Notification Recipients</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Approver Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Copy to</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementer Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Change Detail</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Area: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Type: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Details regarding the change to be requested</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Risk, Migration and Contingencies</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Risk</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Priority (1-4)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Back out plan in place</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Detail of the back out plan</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Timing of Change</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementation date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End date (if applicable)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Free text</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachment</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->


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
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/replenishments%s'>http://%s/replenishments%s</a>
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
        """ % (status, date_time, current_user, Requested_By,DateAndTime,Approver_Details,Copy_to,Implementer_Details,
            Change_Type_ddown,Change_Type_cbox,Change_Type_Detail,Risk,Priority, Back_out_plan, Back_out_plan_details,
            Implementation_date,End_date, ReqComments, attchmnt,reject_link,approve_link,
            domainpath, encoded_param, domainpath, encoded_param)

        msg_body_no_approve_reject = """\
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
                        <p>Hi, <br/><br/><br/>The request for Replenishment Change has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requested By</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Notification Recipients</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Approver Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Copy to</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementer Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Change Detail</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Area: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Type: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Details regarding the change to be requested</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Risk, Migration and Contingencies</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Risk</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Priority (1-4)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Back out plan in place</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Detail of the back out plan</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Timing of Change</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementation date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End date (if applicable)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Free text</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachment</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->


                <!-- Buttons -->
                <!-- Buttons -->

                <!-- Footer -->
                 <tr>
                    <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                    <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                        <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/replenishments%s'>http://%s/replenishments%s</a>
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
        """ % (status, date_time, current_user, Requested_By,DateAndTime,Approver_Details,Copy_to,Implementer_Details,
            Change_Type_ddown,Change_Type_cbox,Change_Type_Detail,Risk,Priority, Back_out_plan, Back_out_plan_details,
            Implementation_date,End_date, ReqComments, attchmnt,
            domainpath, encoded_param, domainpath, encoded_param)
        
        if Copy_to is None or str(Copy_to) == "":
            Copy_to = None

        if Implementer_Details is None or str(Implementer_Details) == "":
            Implementer_Details = None

        if Copy_to is None and Implementer_Details is None:
            mail.send(Approver_Details, subject, msg_body, str(user_email))
        elif Copy_to is not None and Implementer_Details is None:
            # cc = Copy_to + ";" + Implementer_Details
            # Changed to implement the changing of email format to remove the approve/reject buttons
            #mail.send(Approver_Details, subject, msg_body, str(user_email), cc=cc)
            mail.send(Approver_Details, subject, msg_body, str(user_email))
            mail.send(Copy_to, subject, msg_body_no_approve_reject, str(user_email))
        elif Copy_to is None and Implementer_Details is not None:
            # Changed to implement the changing of email format to remove the approve/reject buttons
            #mail.send(Approver_Details, subject, msg_body, str(user_email), cc=cc)
            mail.send(Approver_Details, subject, msg_body, str(user_email))
            mail.send(Implementer_Details, subject, msg_body_no_approve_reject, str(user_email))
        else:
            # Changed to implement the changing of email format to remove the approve/reject buttons
            #mail.send(Approver_Details, subject, msg_body, str(user_email), cc=cc)
            to = Copy_to + ";" + Implementer_Details
            mail.send(Approver_Details, subject, msg_body, str(user_email))
            mail.send(to, subject, msg_body_no_approve_reject, str(user_email))

    @route_with(template='/replenishments/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        item = self.util.decode_key(entity_key).get()

        domain_path = self.session.get('DOMAIN_PATH')
        encoded_param = "?key=" + form_key

        if entity and item:
            approver = item.Approver_Details
        else:
            return 404

        if approver is not None and user == str(approver) and str(item.Approved) == 'Pending':

            Requested_By = item.Requested_By
            DateAndTime = item.DateAndTime
            Approver_Details = item.Approver_Details

            Copy_to = item.Copy_to
            Implementer_Details = item.Implementer_Details
            Change_Type_ddown = item.Change_Type_ddown
            Change_Type_Detail = item.Change_Type_Detail
            Risk = item.Risk
            Priority = item.Priority
            Back_out_plan = item.Back_out_plan
            Back_out_plan_details = item.Back_out_plan_details
            Change_Type_cbox = item.Change_Type_cbox
            Implementation_date = item.Implementation_date
            End_date = item.End_date
            Attachment = item.Attachment
            ReqComments = item.ReqComments
            Details_if_no = "N/A"
            Comments = "N/A"

            if flag == 'Yes':
                stat = 3
                approval = "Yes"
                status = "Approved"
                
            elif flag == 'No':
                stat = 4
                approval = "No"
                status = "Rejected"

            subject = "Replenishment Change Request - " + Change_Type_ddown + " - " + DateAndTime + " - " + status

            item.Approved = approval
            item.put()

            # Send Email
            if flag == 'Yes' or flag == 'No':
                to = Requested_By
                self.sendMail(Requested_By,DateAndTime,Approver_Details,Copy_to,
                        Implementer_Details,Change_Type_ddown,Change_Type_Detail,Risk,Priority,
                        Back_out_plan,Back_out_plan_details, Change_Type_cbox, Implementation_date,
                        End_date, Attachment, ReqComments, Details_if_no, Comments,
                        status, to,subject, domain_path,encoded_param)
            # Redirect
            return self.redirect(self.uri(action='list', key=form_key, status=stat))

        if str(item.Approved) == 'Yes' or str(item.Approved) == 'No':

            return "<br><br><br><center><b>This request has been Approved or Rejected. Back to <a href='http://" + str(domain_path) + "/replenishments" + str(encoded_param) + "&status=all'>list.</a></b></center>"

        else:
            # Approver is no longer assigned to this request being approved or rejected
            return "<br><br><br><center><b>Approver is no longer assigned to this request being approved or rejected. Back to <a href='http://" + str(domain_path) + "/replenishments" + str(encoded_param) + "&status=all'>list.</a></b></center>"
    
    @route
    def sendNotif(self):

        form = self.request.params
        domainpath = self.session.get('DOMAIN_PATH')
        keyid = form['keyid']
        selectedRequest = self.util.decode_key(keyid).get()

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        Requested_By = form['Requested_By']
        DateAndTime = form['DateAndTime']
        Approver_Details = form['Approver_Details']

        Copy_to = selectedRequest.Copy_to
        Implementer_Details = selectedRequest.Implementer_Details
        Change_Type_ddown = selectedRequest.Change_Type_ddown
        Change_Type_Detail = selectedRequest.Change_Type_Detail
        Risk = selectedRequest.Risk
        Priority = selectedRequest.Priority
        Back_out_plan = selectedRequest.Back_out_plan
        Back_out_plan_details = selectedRequest.Back_out_plan_details
        Change_Type_cbox = selectedRequest.Change_Type_cbox
        Implementation_date = selectedRequest.Implementation_date
        End_date = selectedRequest.End_date
        Attachment = selectedRequest.Attachment
        ReqComments = selectedRequest.ReqComments
        
        Approved = form['Approved']
        Details_if_no = form['Details_if_no']
        Comments = form['Comments']

        status = Approved
        
        if status == 'Yes':
            approval = 'Approved'
        else:
            approval = 'Rejected'

        if (Comments == "" or Comments is None):
            Comments = "None"

        if (Details_if_no == "" or Details_if_no is None):
            Details_if_no = "None"

        selectedRequest.Approved = Approved
        selectedRequest.Details_if_no = Details_if_no
        selectedRequest.Comments = Comments
        selectedRequest.put()

        # Will send notifications to the requestor
        to = Requested_By
        subject = "Replenishment Change Request - " + Change_Type_ddown + " - " + DateAndTime + " - " + approval
        
        Replenishments.sendMail(Requested_By,DateAndTime,Approver_Details,Copy_to,
            Implementer_Details,Change_Type_ddown,Change_Type_Detail,Risk,Priority,
            Back_out_plan,Back_out_plan_details, Change_Type_cbox, Implementation_date,
            End_date, Attachment, ReqComments, Details_if_no, Comments,
            approval, to,subject, domainpath,encoded_param)

        return self.redirect(self.uri(action='list', key=form_key))

    @classmethod
    def sendMail(self, Requested_By,DateAndTime,Approver_Details,Copy_to,
            Implementer_Details,Change_Type_ddown,Change_Type_Detail,Risk,Priority,
            Back_out_plan,Back_out_plan_details, Change_Type_cbox, Implementation_date,
            End_date, Attachment, ReqComments, Details_if_no, Comments,
            approval, to,subject, domainpath,encoded_param):

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
                        <p>Hi, <br/><br/><br/>The request for Replenishment Change has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requested By</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Notification Recipients</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Approver Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Copy to</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementer Details</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Change Detail</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Area: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Change Type: Change Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Details regarding the change to be requested</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Risk, Migration and Contingencies</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Risk</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Priority (1-4)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Back out plan in place</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Detail of the back out plan</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 30px 0 10px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">RCR Communication - Timing of Change</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Implementation date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End date (if applicable)</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Free text</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachment</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 row 2 liner -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Details provided if No</span><br/>
                        <p style="color: #262626; font-size: 12px;">%s</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 row 2 liner -->

                <!-- 1 row 2 liner -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Reviewer Additional Comments</span><br/>
                        <p style="color: #262626; font-size: 12px;">%s</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 row 2 liner -->

                <!-- Footer -->
                 <tr>
                    <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                    <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                        <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/replenishments%s'>http://%s/replenishments%s</a>
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
        """ % (approval, date_time, current_user, Requested_By,DateAndTime,Approver_Details,Copy_to,Implementer_Details,
            Change_Type_ddown,Change_Type_cbox,Change_Type_Detail, Risk,Priority, Back_out_plan, Back_out_plan_details,
            Implementation_date,End_date, ReqComments, attchmnt, Details_if_no, Comments, 
            domainpath, encoded_param, domainpath, encoded_param)

        if Copy_to is None and Implementer_Details is None:
            mail.send(to, subject, msg_body, str(users.get_current_user()))
        else:
            cc = Copy_to + ";" + Implementer_Details
            mail.send(to, subject, msg_body, str(users.get_current_user()), cc=cc)
