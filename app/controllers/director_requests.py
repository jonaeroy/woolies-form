from ferris import Controller, scaffold, route_with, route
from ..models.director_request import DirectorRequest
from google.appengine.api import users
from ferris.components.pagination import Pagination
from ferris.core import mail
import logging
import json
from ..controllers.utils import Utils
from ..controllers.users import Users
import datetime
import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from ferris.core.ndb import ndb


class DirectorRequests(Controller):

    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Drafts)
        pagination_limit = 10
        sv_result_variable = 'director_requests'
        sv_status_field = 'status'
        action_form = 'form_add'

    class Scaffold:
        display_properties = ('status', 'created_by', 'created')

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params, self.request)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

    @route_with(template='/director/page/add')
    def form_add(self):
        self.meta.view.template_name = 'director_requests/form.html'

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Test Director Request Form'
        self.context['user_fullname'] = self.session.get('user_fullname')

    def add(self):
        form_key = self.context.get('form_key')
        def before_save(controller, container, item):
            username = self.request.get_all('username[]')
            email_address = self.request.get_all('email_address[]')
            role = self.request.get_all('role[]')
            activity = self.request.get_all('activity[]')
            comment = self.request.get_all('comment[]')

            details = []

            for count in range(len(username)):
                value_1 = Utils.html_escape(username[count])
                value_2 = Utils.html_escape(email_address[count])
                value_3 = Utils.html_escape(role[count])
                value_4 = Utils.html_escape(activity[count])
                value_5 = Utils.html_escape(comment[count])

                if value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "":
                    data = {}
                    data['username'] = value_1
                    data['email_address'] = value_2
                    data['role'] = value_3
                    data['activity'] = value_4
                    data['comment'] = value_5

                    details.append(data)

            item.details = json.dumps(details)

        def after_save(controller, container, item):
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            form_status = 'Sent'
            additional_comments = 'N/A'
            domain_path = self.session.get('DOMAIN_PATH')
            subject = "Test Director Request Notification"

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            # Send an email to the 1st Level Approver
            self.sendMail(form_status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

            # Send an email to the CC'd Address
            to = item.cc
            self.sendMail(form_status, item, additional_comments, to, subject, domain_path, None, encoded_param)

        self.events.scaffold_before_save += before_save
        self.events.scaffold_after_save += after_save
        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route
    def delete(self, key):
        result = self.util.decode_key(key).get()
        result.key.delete()
        frmkey = self.request.params['key']
        tab = self.request.params['status']
        return self.redirect(self.uri(action='delete_suc', key=frmkey, status=tab))

    @route
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        tab = self.request.params['status']
        if tab == 'None':
            tab = 0
        self.context['tab'] = tab
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def list(self):
        usertypekey = self.session.get('user_groups')

        if usertypekey is None:
            usertype = None
        else:
            usertype = self.util.decode_key(usertypekey.urlsafe()).get()

        try:
            self.context['tab'] = self.request.params['status']
        except:
            self.context['tab'] = None

        self.context['usertype'] = usertype
        self.context['frmkey'] = self.session.get(self.name + "_KEY")
        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and DirectorRequest.created_by or -DirectorRequest.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and DirectorRequest.status or -DirectorRequest.status
        else:
            order = self.request.get('order_by_date') == 'desc' and DirectorRequest.created or -DirectorRequest.created

        if showAll:
            self.context['director_requests'] = DirectorRequest.query().order(order)
        else:
            self.context['director_requests'] = DirectorRequest.query(DirectorRequest.created_by == users.get_current_user()).order(order)

        self.context['PAGE_TITLE'] = 'Test Director Request List'
        self.context['isManager'] = self.context.get('user_isManager')
        self.context['sv_director_requests'] = self.context['director_requests']

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route
    def edit_data(self):
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

        form = self.request.params
        key = form['entity_key']
        frmkey = form['frmkey']
        item_data = self.util.decode_key(key).get()

        username = self.request.get_all('username[]')
        email_address = self.request.get_all('email_address[]')
        role = self.request.get_all('role[]')
        activity = self.request.get_all('activity[]')
        comment = self.request.get_all('comment[]')

        details = []

        for count in range(len(username)):
            value_1 = Utils.html_escape(username[count])
            value_2 = Utils.html_escape(email_address[count])
            value_3 = Utils.html_escape(role[count])
            value_4 = Utils.html_escape(activity[count])
            value_5 = Utils.html_escape(comment[count])

            if value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "":
                data = {}
                data['username'] = value_1
                data['email_address'] = value_2
                data['role'] = value_3
                data['activity'] = value_4
                data['comment'] = value_5

                details.append(data)

        item_data.details = json.dumps(details)

        item_data.subject = form['subject']
        item_data.cc = form['cc']
        item_data.domain_name = form['domain_name']
        item_data.project_number_name = form['project_number_name']
        item_data.special_request = form['special_request']
        # item_data.username = form['username']
        # item_data.email_address = form['email_address']
        # item_data.role = form['role']
        # item_data.activity = form['activity']
        # item_data.comment = form['comment']
        item_data.status = int(form['status'])

        entity = item_data.put()

        # Send email after editing #
        to = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
        item = entity.get()
        form_status = 'Edited'
        additional_comments = 'N/A'
        domain_path = self.session.get('DOMAIN_PATH')
        subject = "Change in Test Director Request Notification"

        encoded_param = "?key=" + frmkey

        cc = item.cc

        # Create approve/reject link
        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'tempapprove')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'reject_level_1')

        # Send an email to the 1st Level Approver
        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

        # Send an email to the submitter and to the CC'd address
        to = str(item.created_by)
        self.sendMail(form_status, item, additional_comments, cc, subject, domain_path, cc, encoded_param)

        # return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))
        return self.redirect(self.uri(action='list', key=frmkey))

    @route_with(template='/director_requests/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        item = self.util.decode_key(entity_key).get()
        _list = []
        assignees = None
        approver_group_key = None
        tab = None

        if entity:
            if flag == 'tempapprove':
                approver_group_key = entity.first_level_manager.get().key.urlsafe()
            elif flag == 'approve':
                approver_group_key = entity.second_level_manager.get().key.urlsafe()
            elif flag == 'reject_level_1':
                tab = '4'
                approver_group_key = entity.first_level_manager.get().key.urlsafe()
            elif flag == 'reject_level_2':
                tab = '4'
                approver_group_key = entity.second_level_manager.get().key.urlsafe()

            if approver_group_key is not None:
                assignees = Users.get_user_list_by_group(approver_group_key)
                assignees = assignees.replace(' ', '');

        if assignees is not None:
            _list = assignees.split(";")

        if user in _list:
            domain_path = self.session.get('DOMAIN_PATH')
            encoded_param = "?key=" + form_key
            additional_comments = 'N/A'
            subject = "Test Director Request Approval Notification"
            exp_current_status = None

            if item:
                if flag == 'tempapprove' and item.status == 1:
                    status = 2
                    exp_current_status = 1
                    form_status = 'Temporarily Approved'
                    tab = '2'
                elif flag == 'approve' and item.status == 2:
                    status = 3
                    exp_current_status = 2
                    form_status = "Approved"
                    tab = '3'
                elif flag == 'reject_level_1' and item.status == 1:
                    status = 4
                    exp_current_status = 1
                    subject = "Test Director Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'
                elif flag == 'reject_level_2' and item.status == 2:
                    status = 4
                    exp_current_status = 2
                    subject = "Test Director Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'

                if item.status == exp_current_status:
                    item.status = status
                    item.put()

                    cc = item.cc

                    if cc is None or str(cc) == "":
                        cc = None

                    # Send Email
                    if flag == 'reject_level_1' or flag == 'reject_level_2' or flag == 'approve':
                        to = str(item.created_by)
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, cc, encoded_param)
                    elif flag == 'tempapprove':
                        to = Users.get_user_list_by_group(entity.second_level_manager.get().key.urlsafe())
                        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'approve')
                        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'reject_level_2')

                        # Send an email to the 2nd Level Approver
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

                        # Send email to submitter and to the CC'd address
                        to = str(item.created_by)
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, cc, encoded_param)
                else:
                    return self.components.split_view.already_approved(form_key)
            else:
                return 404

        # Redirect
        if tab is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @route
    def update(self, key):
        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']
        self.context['key'] = key
        self.context['details'] = json.loads(item.details)

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
        self.context['subject'] = result.subject
        self.context['cc'] = result.cc
        self.context['domain_name'] = result.domain_name
        self.context['project_number_name'] = result.project_number_name
        self.context['details'] = json.loads(result.details)
        self.context['special_request'] = result.special_request

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)
        self.context['form_status'] = statusVar

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Director Request View'
        self.context['is_creator'] = is_creator

    @route_with(template='/director_requests/fetch_request_status/<entity_key>')
    def fetch_status(self, entity_key):
        result = self.util.decode_key(entity_key).get()
        return str(result.status)

    @route
    def sendNotif(self):
        form = self.request.params
        tab = None

        action = form['action']
        additional_comments = form['additional_comments']
        keyid = form['keyid']

        result = self.util.decode_key(keyid).get()
        domain_path = self.session.get('DOMAIN_PATH')
        subject = "Test Director Request Approval Notification"

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        cc = result.cc

        if (action == "tempapprove"):
            tab = '2'
            result.status = 2
            result.put()
            form_status = "Temporarily Approved"
            to = Users.get_user_list_by_group(self.context.get('second_group_approver').key.urlsafe())

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'reject_level_2')

            # Send an email to the 1st Level Approver
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

            # Send an email to the submitter and to the CC'd address
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "approve"):
            tab = '3'
            result.status = 3
            result.put()
            form_status = "Approved"
            to = str(result.created_by)  # temporary recipient
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "reject"):
            tab = '4'
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Test Director Request Rejection Notification"
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)

        if tab is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @classmethod
    def sendMail(self, form_status, resource, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link='#', reject_link='#'):
        user_details = ""

        subj = resource.subject
        details = resource.details
        domain_name = resource.domain_name
        project_number_name = resource.project_number_name
        special_request = resource.special_request
        user = 'notifications@woolworths-Forms.appspotmail.com'
        display_cc = resource.cc
        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

        #logging.info(details)

        if details is not None:
            objLoad = json.loads(details)

        for detail in objLoad:
            user_details += "Username: %s" % detail['username'] + "<br>"
            user_details += "Email Address: %s" % detail['email_address'] + "<br>"
            user_details += "Role: %s" % detail['role'] + "<br>"
            user_details += "Activity: %s" % detail['activity'] + "<br>"
            user_details += "Comment: %s" % detail['comment'] + "<br><br>"

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
        else:
            approve_reject_body = '<!-- No Buttons -->'

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
                                <p>Hi, <br/><br/>The request for test director has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        </tr>
                        <!-- opening -->

                         <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Subject</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                         <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">CC:</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                         <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Domain Name</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                         <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Project Number-Name</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                         <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">User Details</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 row 2 liner -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Special Request</span><br/>
                                <p style="color: #262626; font-size: 12px;">%s</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 row 2 liner -->

                        <!-- 1 row 2 liner -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Manager's Comments</span><br/>
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
                                    <a style='color: #909090;' target='_blank' href='http://%s/director_requests%s'>http://%s/director_requests%s</a>
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
                   """ % (form_status, date_time, current_user, subj, display_cc, domain_name, project_number_name,
                        user_details, special_request, additional_comments,
                        approve_reject_body,
                        domain_path, encoded_param, domain_path, encoded_param)

        if str(cc) != "" and cc is not None:
            mail.send(to, subject, msg_body, user, cc=cc)
        else:
            mail.send(to, subject, msg_body, user)
