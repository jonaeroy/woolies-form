from ferris import Controller, scaffold, route_with, route
from ..models.pack_size import PackSize
from ..controllers.users import Users
from ferris.core import mail
from google.appengine.api import users
from ferris.components import pagination
from ..controllers.utils import Utils
import json
import logging
from ferris.components.upload import Upload
import datetime
# import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from ferris.core.ndb import ndb
from google.appengine.ext import blobstore

class PackSizes(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, SplitView, pagination.Pagination, Upload, Drafts, SplitView)
        pagination_limit = 10
        sv_result_variable = 'pack_sizes'
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

    @route_with(template='/pack_sizes/page/add')
    def form_add(self):
        form_key = self.context.get('form_key')
        def before_save(controller, container, item):
            item_number = self.request.get_all('item_number[]')
            item_description = self.request.get_all('item_description[]')
            old_inner = self.request.get_all('old_inner[]')
            old_outer = self.request.get_all('old_outer[]')
            new_inner = self.request.get_all('new_inner[]')
            new_outer = self.request.get_all('new_outer[]')
            comments = self.request.get_all('comments[]')

            details = []

            for count in range(len(item_number)):
                value_1 = item_number[count]
                value_2 = item_description[count]
                value_3 = old_inner[count]
                value_4 = old_outer[count]
                value_5 = new_inner[count]
                value_6 = new_outer[count]
                value_7 = comments[count]

                if value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "" or value_6 != "" or value_7 != "":
                    data = {}

                    data['item_number'] = value_1
                    data['item_description'] = Utils.html_escape(value_2)
                    data['old_inner'] = value_3
                    data['old_outer'] = value_4
                    data['new_inner'] = value_5
                    data['new_outer'] = value_6
                    data['comments'] = Utils.html_escape(value_7)

                    details.append(data)

            item.details = json.dumps(details)

        def after_save(controller, container, item):
            status = 'Sent'
            additional_comments = 'N/A'
            subject = "Masters Inner & Outer Pack Size Change Request Notification"
            # to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            #cc = item.replenisher
            to = item.replenisher
            cc = None

            key = item.key.urlsafe()
            domain_path = self.session.get('DOMAIN_PATH')

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            self.sendMail(status, item, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link, reject_link)

        self.events.scaffold_before_save += before_save
        self.events.scaffold_after_save += after_save
        self.meta.view.template_name = 'pack_sizes/form.html'
        self.context['user'] = self.session.get('user_email')
        self.context['user_fullname'] = self.session.get('user_fullname')
        self.context['PAGE_TITLE'] = 'Masters Inner and Outer Pack Size Change Request Form'

        self.scaffold.redirect = '/pack_sizes?key=' + form_key

        return scaffold.add(self)

    @route_with(template='/pack_sizes/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.status)

    def list(self):
        usertypekey = self.session.get('user_groups')

        if usertypekey is None:
            usertype = None
        else:
            usertype = self.util.decode_key(usertypekey.urlsafe()).get()

        self.context['usertype'] = usertype

        try:
            self.context['tab'] = self.request.params['status']
        except:
            self.context['tab'] = None

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and PackSize.created_by or -PackSize.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and PackSize.status or -PackSize.status
        else:
            order = self.request.get('order_by_date') == 'desc' and PackSize.created or -PackSize.created

        # if showAll:
        #     self.context['pack_sizes'] = PackSize.query().order(order)
        # else:
        #     self.context['pack_sizes'] = PackSize.query(PackSize.created_by == users.get_current_user()).order(order)

        result = PackSize.query().order(order).filter(PackSize.replenisher == str(users.get_current_user().email()).lower())

        if result.get():
            self.context['pack_sizes'] = result
            self.context['is_Merch_Manager'] = True
        else:
            self.context['is_Merch_Manager'] = False
            if showAll:
                self.context['pack_sizes'] = PackSize.query().order(order)
            else:
                self.context['pack_sizes'] = PackSize.query(PackSize.created_by == users.get_current_user()).order(order)

        # return str(result.fetch())

        self.context['PAGE_TITLE'] = 'Masters Inner and Outer Pack Size Change Request List'
        self.context['isManager'] = self.context.get('user_isManager')
        self.context['user'] = self.session.get('user_email')
        self.context['user_isFormAdmin'] = self.context.get('user_isFormAdmin')
        # self.context['frmkey'] = self.request.params['key']
        self.context['frmkey'] = self.session.get(self.name + "_KEY")

        self.context['sv_pack_sizes'] = self.context['pack_sizes']

    @route
    def delete(self, key):
        result = self.util.decode_key(key).get()
        result.key.delete()
        frmkey = self.request.params['key']
        tab = self.request.params['status']
        return self.redirect(self.uri(action='delete_suc', key=frmkey, status=tab))

    @route
    def delete_suc(self):
        self.context['key'] = self.request.params['key']
        tab = self.request.params['status']
        if tab == 'None':
            tab = 0
        self.context['tab'] = tab
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self, key):

        is_creator = False

        result = self.util.decode_key(key).get()

        if str(users.get_current_user()) == str(result.created_by):
            is_creator = True

        self.context['buyer_or_baa_name'] = result.buyer_or_baa_name
        self.context['replenisher'] = result.replenisher
        self.context['viewer'] = result.viewer
        self.context['reason_for_change'] = result.reason_for_change
        self.context['department'] = result.department
        self.context['supplier_number'] = result.supplier_number
        self.context['submission_date'] = result.submission_date
        self.context['supplier_name'] = result.supplier_name
        self.context['effective_date'] = result.effective_date
        self.context['dsd_or_dc'] = result.dsd_or_dc
        self.context['details'] = json.loads(result.details)
        self.context['notes'] = result.notes

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)
        self.context['form_status'] = statusVar
        self.context['download_link'] = Utils.generate_download_link(result.attachment)

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Masters Inner and Outer Pack Size Change Request View'
        self.context['keyid'] = result.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['is_creator'] = is_creator

    @route_with(template='/pack_sizes/page/edit/<key>/<form_key>')
    def edit_data(self, key, form_key):

        item = self.util.decode_key(key).get()

        attachment = None

        if item.attachment is not None:
            attachment = blobstore.BlobInfo.get(item.attachment)
            attachment = attachment.filename

        self.context['item'] = item
        self.context['details'] = json.loads(item.details)
        self.context['attachment'] = attachment

        def before_save(controller, container, item):

            item_number = self.request.get_all('item_number[]')
            item_description = self.request.get_all('item_description[]')
            old_inner = self.request.get_all('old_inner[]')
            old_outer = self.request.get_all('old_outer[]')
            new_inner = self.request.get_all('new_inner[]')
            new_outer = self.request.get_all('new_outer[]')
            comments = self.request.get_all('comments[]')

            details = []

            for count in range(len(item_number)):
                value_1 = item_number[count]
                value_2 = item_description[count]
                value_3 = old_inner[count]
                value_4 = old_outer[count]
                value_5 = new_inner[count]
                value_6 = new_outer[count]
                value_7 = comments[count]

                if value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "" or value_6 != "" or value_7 != "":
                    data = {}

                    data['item_number'] = value_1
                    data['item_description'] = Utils.html_escape(value_2)
                    data['old_inner'] = value_3
                    data['old_outer'] = value_4
                    data['new_inner'] = value_5
                    data['new_outer'] = value_6
                    data['comments'] = Utils.html_escape(value_7)

                    details.append(data)

            item.details = json.dumps(details)

        self.events.scaffold_before_save += before_save
        self.meta.view.template_name = 'pack_sizes/update.html'
        self.scaffold.redirect = '/pack_sizes?key=' + form_key

        self.context['frmkey'] = form_key
        self.context['key'] = key

        # Send email after editing #
        def after_save(controller, container, item):
            status = 'Edited'
            additional_comments = 'N/A'
            subject = "Change in Masters Inner & Outer Pack Size Change Request Notification"

            encoded_param = "?key=" + form_key

            to = item.replenisher
            cc = None

            domain_path = self.session.get('DOMAIN_PATH')

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            self.sendMail(status, item, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link, reject_link)

        self.events.scaffold_after_save += after_save

        return scaffold.edit(self, key)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/pack_sizes/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        entity = ndb.Key(urlsafe=form_key).get()
        user = str(users.get_current_user())
        item = self.util.decode_key(entity_key).get()
        _list = []
        is_second_group_approver = False
        replenisher = None
        approver_group_key = None
        assignees = None
        tab = None

        if entity:
            if flag == 'tempapprove':
                replenisher = item.replenisher
            elif flag == 'approve':
                approver_group_key = entity.second_level_manager.get().key.urlsafe()
                is_second_group_approver = True
            elif flag == 'reject_level_1':
                tab = '4'
                # approver_group_key = entity.first_level_manager.get().key.urlsafe()
                replenisher = item.replenisher
            elif flag == 'reject_level_2':
                tab = '4'
                approver_group_key = entity.second_level_manager.get().key.urlsafe()

            if approver_group_key is not None:
                assignees = Users.get_user_list_by_group(approver_group_key)
                assignees = assignees.replace(' ', '');

        if assignees is not None:
            _list = assignees.split(";")
        elif replenisher is not None:
            _list = replenisher.split(";")

        # Validation if user is in Approver Group 1 or 2
        if user in _list:
            domain_path = self.session.get('DOMAIN_PATH')
            encoded_param = "?key=" + form_key
            additional_comments = 'N/A'
            subject = "Masters Inner and Outer Pack Size Change Request Approval Notification"
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
                    subject = "Masters Inner and Outer Pack Size Change Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'
                elif flag == 'reject_level_2' and item.status == 2:
                    status = 4
                    exp_current_status = 2
                    subject = "Masters Inner and Outer Pack Size Change Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'

                if item.status == exp_current_status:
                    item.status = status
                    item.put()

                    cc = None
                    viewer = item.viewer

                    if viewer is not None and viewer != "":
                        viewer = ";" + str(viewer)
                    else:
                        viewer = ""

                    # Send Email
                    if flag == 'reject_level_1' or flag == 'reject_level_2' or flag == 'approve':
                        to = str(item.created_by)

                        if is_second_group_approver:
                            to += viewer

                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, cc, encoded_param)
                    elif flag == 'tempapprove':
                        to = "mastersmerchsupport@woolworths.com.au"
                        # to = "formapprover2@woolworths.com.au"
                        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'approve')
                        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'reject_level_2')

                        # Send email to approver
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link, reject_link)

                        # Send email to form sumbmitter
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
    def sendNotif(self):
        form = self.request.params
        tab = None

        action = form['action']
        additional_comments = form['additional_comments']
        keyid = form['keyid']

        result = self.util.decode_key(keyid).get()
        domain_path = self.session.get('DOMAIN_PATH')
        subject = "Masters Inner and Outer Pack Size Change Request Approval Notification"

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        is_first_group_approver = self.context.get('is_first_group_approver')
        is_second_group_approver = self.context.get('is_second_group_approver')

        # cc = result.replenisher
        cc = None
        viewer = result.viewer

        if viewer is not None and viewer != "":
            viewer = ";" + str(viewer)
        else:
            viewer = ""

        if is_first_group_approver:
            cc = None

        if (action == "tempapprove"):
            tab = '2'
            result.status = 2
            result.put()
            form_status = "Temporarily Approved"
            # to = Users.get_user_list_by_group(self.context.get('second_group_approver').key.urlsafe())
            to = "mastersmerchsupport@woolworths.com.au" # This is the latest fixed approver level 2
            # to = "formapprover2@woolworths.com.au;"

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'reject_level_2')

            # Send email to the approver level 2
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link, reject_link)

            # Send email to the form submitter
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "approve"):
            tab = '3'
            result.status = 3
            result.put()
            form_status = "Approved"
            to = str(result.created_by)

            if is_second_group_approver:
                to += viewer

            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "reject"):
            tab = '4'
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Masters Inner and Outer Pack Size Change Request Rejection Notification"
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)

        if tab is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @classmethod
    def sendMail(self, form_status, resource, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link='#', reject_link='#'):

        items = ""
        details = resource.details
        buyer_or_baa_name = resource.buyer_or_baa_name
        replenisher = resource.replenisher
        viewer = resource.viewer
        reason_for_change = resource.reason_for_change
        department = resource.department
        supplier_number = resource.supplier_number
        supplier_name = resource.supplier_name
        submission_date = resource.submission_date
        effective_date = resource.effective_date
        dsd_or_dc = resource.dsd_or_dc
        notes = resource.notes
        attachment = Utils.generate_download_link(resource.attachment)
        user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

        if details is not None:
            objLoad = json.loads(details)

            #logging.info(objLoad)

            for detail in objLoad:
                items += """\
                        Item Number - %s <br>
                        Item Description - %s <br>
                        Old Inner - %s <br>
                        Old Outer - %s <br>
                        New Inner - %s <br>
                        New Outer - %s <br>
                        Comments - %s <br><br>
                        """ % (detail['item_number'], detail['item_description'], detail['old_inner'], detail['old_outer'], detail['new_inner'], detail['new_outer'], detail['comments'])

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
                                    <p>Hi, <br/><br/><br/>The request for inner & outer pack size change has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                            </tr>
                            <!-- opening -->

                            <!-- 1 liner tall row important -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Buyer or BAA Name</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner tall row important -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Replenisher</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner tall row important -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Viewer</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Department</span>
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
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Reason for Change</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Supplier Number</span>
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
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Supplier Name</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 liner 2 columns -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Submission Date</span>
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
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Effective Date</span>
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
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">DSD or DC</span>
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
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Details</span><br/>
                                    <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 liner tall row important -->

                            <!-- 1 row 2 liner -->
                            <tr>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                                <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                    <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Notes</span><br/>
                                    <p style="color: #262626; font-size: 12px;">%s</p>
                                </td>
                                <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            </tr>
                            <!-- 1 row 2 liner -->

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
                                        <a style='color: #3b9ff3;' target='_blank' href='http://%s/pack_sizes%s'>http://%s/pack_sizes%s</a>
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

                   """ % (form_status, date_time, user, buyer_or_baa_name, replenisher, viewer, department,
                        reason_for_change, supplier_number, supplier_name, submission_date, effective_date,
                        dsd_or_dc, items, notes, attachment, additional_comments,
                        approve_reject_body,
                        domain_path, encoded_param, domain_path, encoded_param)

        if str(cc) != "" and cc is not None:
            mail.send(to, subject, msg_body, user, cc=cc)
        else:
            mail.send(to, subject, msg_body, user)
