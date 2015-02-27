from ferris import Controller, messages, route_with, route
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from app.models.bnld import Bnld
import json
'''
from google.appengine.api import users
from ..controllers.users import Users
from ferris.core import mail
from ..controllers.utils import Utils

import logging
from ferris.core.ndb import ndb
'''
import datetime

'''
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from google.appengine.ext import blobstore
'''

class Bnlds(Controller):

    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        pagination_limit = 10
        '''
        sv_result_variable = 'bnlds'
        sv_status_field = 'Status'
        action_form = 'bnldform'
        '''
        Model = Bnld


        
    '''
    class Scaffold:
        display_properties = ('created_by', 'created', 'Buyer_or_BAA_Name',
            'Date','Merchandise_Manager','Number_of_Items','Include_Any_Comments_Below')
    '''
    '''
    @route_with('/api/messages/store:<store_num>/<department>/<location>/sort_by:<sort_by>/from:<start_date>/to:<end_date>', methods=['GET'])
   @route_with('/api/messages/store:<store_num>/<department>/<location>/sort_by:<sort_by>', methods=['GET'])
   @route_with('/api/messages/store:<store_num>/<department>/<location>/from:<start_date>/to:<end_date>', methods=['GET'])
   @route_with('/api/messages/store:<store_num>/<department>/<location>', methods=['GET'])
   def api_list_store_department(self, store_num, department, location, sort_by=None, start_date=None, end_date=None):
    
    '''
    

    
    @route_with('/bnlds/list', methods=['GET'])
    def list(self):
        self.meta.view.template_name = 'angular/bnlds/list.html'

    @route
    def form(self):
        self.meta.view.template_name = 'angular/bnlds/bnldform.html'

    @route_with('/api/bnlds', methods=['GET'])
    def api_list(self):
        self.context['data'] = Bnld.list_all()

    @route_with('/api/bnlds', methods=['POST'])
    def api_create(self):
        params = json.loads(self.request.body)
        self.context['data'] = Bnld.create(params)

    @route_with('/api/bnlds:<key>', methods=['GET'])
    def api_get(self, key):
        self.context['data'] = self.util.decode_key(key).get()

    @route_with('/api/bnlds/:<key>', methods=['POST'])
    def api_update(self, key):
        params = json.loads(self.request.body)
        bnld = self.util.decode_key(key).get()
        bnld.update(params)
        self.context['data'] = bnld

    @route_with('/api/bnlds:<key>', methods=['DELETE'])
    def api_delete(self, key):
        bnld = self.util.decode_key(key).get()
        bnld.delete()
        return 200



    '''
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
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def bnldform(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = item
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'reject_level_1')
            action = "new"

            Bnlds.sendNotifFromUser(form,user_email,domainpath,encoded_param,approve_link,reject_link, action)

        self.events.scaffold_after_save += after_save
        self.context['user'] = self.session.get('user_email')
        for key, value in self.session.items():
            self.context[key] = value

        self.scaffold.redirect = '/bnlds?key=' + form_key
        return scaffold.add(self)


    @route_with(template='/bnlds/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.Status)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/bnlds/page/edit/<key>/<form_key>')
    def edit_data(self, key, form_key):
        item = self.util.decode_key(key).get()

        if item.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below is not None:
            attachment = blobstore.BlobInfo.get(item.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below)
            attachment = attachment.filename
            self.context['attachment'] = attachment
        else:
            self.context['attachment'] = None

        self.context['item'] = item
        self.context['frmkey'] = form_key
        self.context['key'] = key

        self.meta.view.template_name = 'bnlds/update.html'
        self.scaffold.redirect = '/bnlds?key=' + form_key

        def after_save(controller, container, item):
            form = item
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domainpath, self.name, key, form_key, 'reject_level_1')
            action = "edit"

            self.sendNotifFromUser(form,user_email,domainpath,encoded_param, approve_link, reject_link, action)

        self.events.scaffold_after_save += after_save

        return scaffold.edit(self, key)

    @route
    def search(self):

        form = self.request.params

        searchtxt = form['searchtxt']
        searchby = form['searchby']

        logging.info('SEARCH PARAMS ==========> ' + str(searchtxt) + " " + str(searchby))

        result = Bnld.query().filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())

        if result.get():
            # dynamic way - Ray
            # result = Bnld.query(Bnld._properties[searchby] == str(searchtxt)).filter(Bnlds.Manager == str(users.get_current_user().email()).lower())
            # if result.get():
            #         self.context['bnlds'] = result
            if searchby == "Buyer_or_BAA_Name":
                Buyer_or_BAA_Name_result = Bnld.query().filter(Bnld.Buyer_or_BAA_Name == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Buyer_or_BAA_Name_result.get():
                    self.context['bnlds'] = Buyer_or_BAA_Name_result
            elif searchby == "Date":
                Date_result = Bnld.query().filter(Bnld.Date == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Date_result.get():
                    self.context['bnlds'] = Date_result
            elif searchby == "Merchandise_Manager":
                Merchandise_Manager_result = Bnld.query().filter(Bnld.Merchandise_Manager == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Merchandise_Manager_result.get():
                    self.context['bnlds'] = Merchandise_Manager_result
            elif searchby == "Number_of_Items":
                Number_of_Items_result = Bnld.query().filter(Bnld.Number_of_Items == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Number_of_Items_result.get():
                    self.context['bnlds'] = Number_of_Items_result
            elif searchby == "All_New_Lines_Passed_Validation":
                All_New_Lines_Passed_Validation_result = Bnld.query().filter(Bnld.All_New_Lines_Passed_Validation == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if All_New_Lines_Passed_Validation_result.get():
                    self.context['bnlds'] = All_New_Lines_Passed_Validation_result
            elif searchby == "QA_Acceptance":
                QA_result = Bnld.query().filter(Bnld.QA_Acceptance == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if QA_result.get():
                    self.context['bnlds'] = QA_result
            elif searchby == "MSDS":
                MSDS_result = Bnld.query().filter(Bnld.MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if MSDS_result.get():
                    self.context['bnlds'] = MSDS_result
            elif searchby == "Comments":
                Comments_result = Bnld.query().filter(Bnld.Include_Any_Comments_Below == str(searchtxt)).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Comments_result.get():
                    self.context['bnlds'] = Comments_result
            else:
                stxt = Utils.revertStatus(searchtxt)
                Status_result = Bnld.query().filter(Bnld.Status == stxt).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())
                if Status_result.get():
                    self.context['bnlds'] = Status_result
        else:

            if searchby == "Buyer_or_BAA_Name":
                Buyer_or_BAA_Name_result = Bnld.query().filter(Bnld.Buyer_or_BAA_Name == str(searchtxt))
                if Buyer_or_BAA_Name_result.get():
                    self.context['bnlds'] = Buyer_or_BAA_Name_result
            elif searchby == "Date":
                Date_result = Bnld.query().filter(Bnld.Date == str(searchtxt))
                if Date_result.get():
                    self.context['bnlds'] = Date_result
            elif searchby == "Merchandise_Manager":
                Merchandise_Manager_result = Bnld.query().filter(Bnld.Merchandise_Manager == str(searchtxt))
                if Merchandise_Manager_result.get():
                    self.context['bnlds'] = Merchandise_Manager_result
            elif searchby == "Number_of_Items":
                Number_of_Items_result = Bnld.query().filter(Bnld.Number_of_Items == str(searchtxt))
                if Number_of_Items_result.get():
                    self.context['bnlds'] = Number_of_Items_result
            elif searchby == "All_New_Lines_Passed_Validation":
                All_New_Lines_Passed_Validation_result = Bnld.query().filter(Bnld.All_New_Lines_Passed_Validation == str(searchtxt))
                if All_New_Lines_Passed_Validation_result.get():
                    self.context['bnlds'] = All_New_Lines_Passed_Validation_result
            elif searchby == "QA_Acceptance":
                QA_result = Bnld.query().filter(Bnld.QA_Acceptance == str(searchtxt))
                if QA_result.get():
                    self.context['bnlds'] = QA_result
            elif searchby == "MSDS":
                MSDS_result = Bnld.query().filter(Bnld.MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines == str(searchtxt))
                if MSDS_result.get():
                    self.context['bnlds'] = MSDS_result
            elif searchby == "Comments":
                Comments_result = Bnld.query().filter(Bnld.Include_Any_Comments_Below == str(searchtxt))
                if Comments_result.get():
                    self.context['bnlds'] = Comments_result
            else:
                stxt = Utils.revertStatus(searchtxt)
                Status_result = Bnld.query().filter(Bnld.Status == stxt)
                if Status_result.get():
                    self.context['bnlds'] = Status_result

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        self.context['frmkey']  = self.request.params['key']

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Bnld.created_by or -Bnld.created_by
        elif self.request.get('order_by_status')    :
            order = self.request.get('order_by_status') == 'desc'  and Bnld.Status or -Bnld.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Bnld.created or -Bnld.created

        result = Bnld.query().order(order).filter(Bnld.Merchandise_Manager == str(users.get_current_user().email()).lower())

        if result.get():

            self.context['bnlds'] = result
            self.context['is_Merch_Manager'] = True
        else:
            self.context['is_Merch_Manager'] = False
            if showAll:
                self.context['bnlds'] = Bnld.query().order(order)
            else:
                query = Bnld.query(Bnld.created_by == users.get_current_user()).order(order)

                self.context['bnlds'] = query

            self.context['sv_bnlds'] = self.context['bnlds']
            

    def view(self,key):

        bnld = self.util.decode_key(key).get()
        current_user = self.session.get('user_email')

        self.context['modified_by'] = bnld.modified_by
        self.context['modified'] = bnld.modified
        self.context['buyer'] = bnld.Buyer_or_BAA_Name
        self.context['cdate'] = bnld.Date
        self.context['merchMngr'] = bnld.Merchandise_Manager
        self.context['numitems'] = bnld.Number_of_Items
        self.context['anlpv'] = bnld.All_New_Lines_Passed_Validation
        self.context['qa'] = bnld.QA_Acceptance
        self.context['msds'] = bnld.MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines
        self.context['comments'] = bnld.Include_Any_Comments_Below
        self.context['attachment'] = bnld.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below

        self.context['download_link'] = Utils.generate_download_link(bnld.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below)

        statusVar = bnld.Status
        self.context['intStatus'] = statusVar
        self.context['status'] = Utils.convertStatus(statusVar)

        self.context['keyid'] = bnld.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']

        if str(current_user) == str(bnld.created_by):
            self.context['is_requestor'] = True
        else:
            self.context['is_requestor'] = False

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotifFromUser(self,form,user_email, domainpath, encoded_param, approve_link, reject_link, action):

        buyer = form.Buyer_or_BAA_Name
        merchmngr = form.Merchandise_Manager
        date = Utils.localize_datetime(datetime.datetime.now())
        numitems = form.Number_of_Items
        anlpv = form.All_New_Lines_Passed_Validation
        qa = form.QA_Acceptance
        msds = form.MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines
        comments = form.Include_Any_Comments_Below
        attchmnt = form.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below

        if action == "edit":
            subject = "Change in Buyers New Line Declaration Request Notification"
            status = 'Edited'
        else:
            status = "Sent"
            subject = "Buyers New Line Declaration Request Notification"

        # Send email notification to Merchandise Manager

        Bnlds.sendMailFromUser(buyer, merchmngr, date, numitems, anlpv, qa, msds, comments, attchmnt, status, subject, user_email, domainpath,encoded_param,approve_link, reject_link)

    @classmethod
    def sendMailFromUser(self,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,status,subject,user_email, domain_path,encoded_param,approve_link, reject_link):

        attchmnt = Utils.generate_download_link(attchmnt)
        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

        msg_body = """\
        <html>
        <body>
            <span style="width: 600px; padding: 1px; background: #d3d3d3; display: block;">
            <table style="padding: 0; margin: 0; width:600px; font-family:Arial,Helvetica,sans-serif; font-size: 12px; letter-spacing: 1px; border-spacing: 0; background-color: #fff;" border="0">
                <tbody>
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px; ">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 50px;">
                            <p style="color: #909090; font-size: 10px; text-align: center;"><em>This is an auto-generated e-mail. Please don't reply</em></p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;">&nbsp;</td>
                    </tr>

                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 150px; background: #2c3742; color: #fff; text-align: justify;">
                            <p>Hi, <br/><br/><br/>The request for Buyer's New Line Decalaration has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span>
                                by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>

                    <tr style="">
                        <td style="padding-top: 40px; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ITEMS </span>
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">BUYER'S EMAIL ADDRESS</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">MERCHANDISE MANAGER</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ALL NEW LINES PASSED VALIDATION</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">QA ACCEPTANCE</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">MSDS Report Loaded onto Chemwatch <br/>for all Applicable Lines</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">COMMENTS</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">Attachment</span><br/>
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
                            <p style="color: #909090; font-size: 12px; text-align: left;">Click here for the Woolies: <strong>Buyer's New Line Declaration Request List</strong>
                                <a href='http://%s/bnlds%s'>http://%s/bnlds%s'</a>
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
        </body>
        </html>
        """ % (status, date_time, current_user, numitems,date,buyer,merchmngr,anlpv,qa,msds,comments,attchmnt,reject_link,approve_link,domain_path,encoded_param,domain_path,encoded_param)

        mail.send(merchmngr, subject, msg_body, str(user_email))

    @route_with(template='/bnlds/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        item = self.util.decode_key(entity_key).get()
        _list = []
        assignees = None
        status = None
        approver_group_key = None


        if entity and item:

            if flag == 'tempapprove':
                merchmanager = item.Merchandise_Manager
            elif flag == 'approve':
                approver_group_key = entity.second_level_manager.get().key.urlsafe()
            elif flag == 'reject_level_1':
                status = '4'
                # approver_group_key = entity.first_level_manager.get().key.urlsafe()
                merchmanager = item.Merchandise_Manager
            elif flag == 'reject_level_2':
                approver_group_key = entity.second_level_manager.get().key.urlsafe()

            if approver_group_key is not None:
                assignees = Users.get_user_list_by_group(approver_group_key)
                assignees = assignees.replace(' ', '');

                logging.info('APPROVERS BEFORE SPLIT ================>' + str(assignees))

        else:

            return 404

        if assignees is not None:
            _list = assignees.split(";")
        elif merchmanager is not None:
            _list = merchmanager.split(";")

        if user in _list:

            logging.info('USER IS IN LIST ================>' + str(user))
            domain_path = self.session.get('DOMAIN_PATH')
            encoded_param = "?key=" + form_key
            additional_comments = 'N/A'
            exp_current_status = None
            subject = "Buyer's New Line Declaration Form Approval Notification"


            if flag == 'tempapprove' and item.Status == 1:
                status = 2
                exp_current_status = 1
                form_status = 'Temporarily Approved'
            elif flag == 'approve' and item.Status == 2:
                status = 3
                exp_current_status = 2
                form_status = "Approved"
            elif flag == 'reject_level_1' and item.Status == 1:
                status = 4
                exp_current_status = 1
                subject = "Buyer's New Line Declaration Request Rejection Notification"
                form_status = "Rejected"
            elif flag == 'reject_level_2' and item.Status == 2:
                status = 4
                exp_current_status = 2
                subject = "Buyer's New Line Declaration Request Rejection Notification"
                form_status = "Rejected"

            if item.Status == exp_current_status:

                item.Status = status
                item.put()

                buyer = item.Buyer_or_BAA_Name
                merchmngr = item.Merchandise_Manager
                date = item.Date
                numitems = item.Number_of_Items
                anlpv = item.All_New_Lines_Passed_Validation
                qa = item.QA_Acceptance
                msds = item.MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines
                comments = item.Include_Any_Comments_Below
                attchmnt = item.Please_attach_the_New_Line_Submission_Sheet_to_this_Form_Below

                # Send Email
                if flag == 'reject_level_1' or flag == 'reject_level_2' or flag == 'approve':

                    to_creator = str(item.created_by)
                    self.sendMailToCreator(form_status, buyer, merchmngr, date, numitems, anlpv, qa, msds, comments, attchmnt, additional_comments, to_creator, subject, domain_path, encoded_param)

                elif flag == 'tempapprove':

                    to_approver = "mastersmerchsupport@woolworths.com.au;"
                    #to_approver = "formapprover2@woolworths.com.au;"
                    to_creator = str(item.created_by)
                    approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'approve')
                    reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'reject_level_2')
                    self.sendMailFromApprover(form_status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to_approver,subject, domain_path,encoded_param,approve_link, reject_link)
                    self.sendMailToCreator(form_status, buyer, merchmngr, date, numitems, anlpv, qa, msds, comments, attchmnt, additional_comments, to_creator, subject, domain_path, encoded_param)

            else:
                return "<br><br><br><center><b>This request has been Approved or Rejected. Back to <a href='http://" + str(domain_path) + "/bnlds" + str(encoded_param) + "&status=all'>list.</a></b></center>"

        # Redirect
        if status is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=status))

    @route
    def sendNotif(self):

        form = self.request.params
        keyid = form['keyid']
        action = str(form['action'])
        buyer = form['buyer']
        merchmngr = form['merchmngr']
        date = str(form['date'])
        numitems = form['numitems']
        anlpv = form['anlpv']
        qa = form['qa']
        msds = form['msds']
        comments = form['comments']
        attchmnt = form['attchmnt']
        status = form['status']
        additional_comments = form['addcomments']
        #tmpto = self.context.get('second_group_approver').key.urlsafe()
        #merchTeam = Users.get_user_list_by_group(tmpto)
        merchTeam = 'mastersmerchsupport@woolworths.com.au'
        #merchTeam = 'formapprover2@woolworths.com.au'

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key
        domain_path = self.session.get('DOMAIN_PATH')

        bnld = self.util.decode_key(keyid).get()

        if (comments == "" or comments is None):
            comments = "None"

        if (additional_comments == "" or additional_comments is None):
            additional_comments = "None"

        stat = 0

        # For Replenishment Approval
        if (action == "tempapprove"):

            # Will send notifications to requestor and merchandising team for temp approval
            to_creator = buyer
            to_approver = merchTeam

            stat = 2
            bnld.Status = stat
            bnld.put()
            status = "Temporarily Approved"
            subject = "Buyer's New Line Declaration Form Approval Notification"
            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'reject')

            Bnlds.sendMailFromApprover(status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to_approver,subject, domain_path,encoded_param,approve_link, reject_link)
            Bnlds.sendMailToCreator(status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to_creator,subject, domain_path,encoded_param)
        # For Merchandising Team Approval
        if (action == "approve"):

            stat = 3
            to = buyer
            bnld.Status = stat
            bnld.put()
            status = "Approved"
            subject = "Buyer's New Line Declaration Form Approval Notification"
            Bnlds.sendMailToCreator(status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to,subject, domain_path,encoded_param)

        # For Replenishment and Merchandise Team Rejection
        elif (action == "reject"):

            stat = 4
            to = buyer
            bnld.Status = stat
            bnld.put()
            status = "Rejected"
            subject = "Buyer's New Line Declaration Form Rejection Notification"
            Bnlds.sendMailToCreator(status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to,subject, domain_path,encoded_param)

        return self.redirect(self.uri(action='list', key=form_key, status=stat))

    @classmethod
    def sendMailFromApprover(self,status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to,subject, domain_path,encoded_param,approve_link, reject_link):

        if attchmnt is None:
            attchmnt = "None"
        else:
            attchmnt = Utils.generate_download_link(attchmnt)

        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

        msg_body = """\

        <html>
        <body>
            <span style="width: 600px; padding: 1px; background: #d3d3d3; display: block;">
            <table style="padding: 0; margin: 0; width:600px; font-family:Arial,Helvetica,sans-serif; font-size: 12px; letter-spacing: 1px; border-spacing: 0; background-color: #fff;" border="0">
                <tbody>
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px; ">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 50px;">
                            <p style="color: #909090; font-size: 10px; text-align: center;"><em>This is an auto-generated e-mail. Please don't reply</em></p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;">&nbsp;</td>
                    </tr>

                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 150px; background: #2c3742; color: #fff; text-align: justify;">
                            <p>Hi, <br/><br/><br/>The request for Buyer's New Line Decalaration has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span>
                                by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>

                    <tr style="">
                        <td style="padding-top: 40px; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ITEMS </span>
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">BUYER'S EMAIL ADDRESS</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">MERCHANDISE MANAGER</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ALL NEW LINES PASSED VALIDATION</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">QA ACCEPTANCE</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">MSDS Report Loaded onto Chemwatch <br/>for all Applicable Lines</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">COMMENTS FROM USER</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 row 2 liner -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">COMMENTS FROM APPROVER</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">Attachment</span><br/>
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
                            <p style="color: #909090; font-size: 12px; text-align: left;">Click here for the Woolies: <strong>Buyer's New Line Declaration Request List</strong>
                                <a href='http://%s/bnlds%s'>http://%s/bnlds%s'</a>
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
        </body>
        </html>
        """ % (status, date_time, current_user, numitems,date,buyer,merchmngr,anlpv,qa,msds,comments,additional_comments,attchmnt,
            reject_link,approve_link,domain_path,encoded_param,domain_path,encoded_param)

        mail.send(to, subject, msg_body, str(users.get_current_user()))

    @classmethod
    def sendMailToCreator(self,status,buyer,merchmngr,date,numitems,anlpv,qa,msds,comments,attchmnt,additional_comments,to,subject, domain_path,encoded_param):

        if attchmnt is None:
            attchmnt = Utils.generate_download_link(attchmnt)
        else:
            attchmnt = "None"
        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

        msg_body = """\
        <html>
        <body>
            <span style="width: 600px; padding: 1px; background: #d3d3d3; display: block;">
            <table style="padding: 0; margin: 0; width:600px; font-family:Arial,Helvetica,sans-serif; font-size: 12px; letter-spacing: 1px; border-spacing: 0; background-color: #fff;" border="0">
                <tbody>
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px; ">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 50px;">
                            <p style="color: #909090; font-size: 10px; text-align: center;"><em>This is an auto-generated e-mail. Please don't reply</em></p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;">&nbsp;</td>
                    </tr>

                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 150px; background: #2c3742; color: #fff; text-align: justify;">
                            <p>Hi, <br/><br/><br/>The request for Buyer's New Line Decalaration has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span>
                                by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>

                    <tr style="">
                        <td style="padding-top: 40px; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ITEMS </span>
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="color: #b85e80; font-weight: bold;">%s</span>
                        </td>
                        <td style="padding: 40px 0 20px 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">BUYER'S EMAIL ADDRESS</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">MERCHANDISE MANAGER</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">ALL NEW LINES PASSED VALIDATION</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">QA ACCEPTANCE</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">MSDS Report Loaded onto Chemwatch <br/>for all Applicable Lines</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">COMMENTS FROM USER</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 row 2 liner -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">COMMENTS FROM APPROVER</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold;">Attachment</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- Footer -->
                     <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                            <p style="color: #909090; font-size: 12px; text-align: left;">Click here for the Woolies: <strong>Buyer's New Line Declaration Request List</strong>
                                <a href='http://%s/bnlds%s'>http://%s/bnlds%s'</a>
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
        </body>
        </html>
        """ % (status,date_time,current_user,numitems,date,buyer,merchmngr,anlpv,qa,msds,comments,additional_comments,attchmnt,
            domain_path,encoded_param,domain_path,encoded_param)


        mail.send(to, subject, msg_body, str(users.get_current_user()))

    '''
