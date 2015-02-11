from ferris import Controller, scaffold, route_with, route
from ferris.core import mail
from google.appengine.api import users
from ferris.components.pagination import Pagination
from ..models.multiple_change import MultipleChange
from ..controllers.utils import Utils
from ..controllers.users import Users
import json
# import logging
import datetime
import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from ferris.core.ndb import ndb

class MultipleChanges(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Drafts, SplitView)
        pagination_limit = 10
        sv_result_variable = 'multiple_changes'
        sv_status_field = 'status'
        action_form = 'add_form'

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

    def add(self):
        form_key = self.context.get('form_key')

        def before_save(controller, container, item):
            item_number = self.request.get_all('item_number[]')
            item_description = self.request.get_all('item_description[]')
            indent_v_domestic = self.request.get_all('indent_v_domestic[]')
            old_som = self.request.get_all('old_som[]')
            new_som = self.request.get_all('new_som[]')
            buyer = self.request.get_all('buyer[]')
            sps = self.request.get_all('sps[]')
            outer_pack = self.request.get_all('outer_pack[]')
            ti = self.request.get_all('ti[]')
            hi = self.request.get_all('hi[]')
            weight = self.request.get_all('weight[]')
            order_point = self.request.get_all('order_point[]')
            pallet_quantity = self.request.get_all('pallet_quantity[]')
            comments = self.request.get_all('comments[]')

            details = []

            for count in range(len(item_number)):
                value_1 = Utils.html_escape(item_number[count])
                value_2 = Utils.html_escape(item_description[count])
                value_3 = indent_v_domestic[count]
                value_4 = old_som[count]
                value_5 = new_som[count]
                value_6 = Utils.html_escape(buyer[count])
                value_7 = Utils.html_escape(sps[count])
                value_8 = Utils.html_escape(outer_pack[count])
                value_9 = Utils.html_escape(ti[count])
                value_10 = Utils.html_escape(hi[count])
                value_11 = Utils.html_escape(weight[count])
                value_12 = Utils.html_escape(order_point[count])
                value_13 = Utils.html_escape(pallet_quantity[count])
                value_14 = Utils.html_escape(comments[count])

                if (value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "" or value_6 != "" or value_7 != "" or
                        value_8 != "" or value_9 != "" or value_10 != "" or value_11 != "" or value_12 != "" or value_13 != "" or value_14 != ""):

                    data = {}
                    data['item_number'] = value_1
                    data['item_description'] = value_2
                    data['indent_v_domestic'] = value_3
                    data['old_som'] = value_4
                    data['new_som'] = value_5
                    data['buyer'] = value_6
                    data['sps'] = value_7
                    data['outer_pack'] = value_8
                    data['ti'] = value_9
                    data['hi'] = value_10
                    data['weight'] = value_11
                    data['order_point'] = value_12
                    data['pallet_quantity'] = value_13
                    data['comments'] = value_14

                details.append(data)

            item.details = json.dumps(details)

        def after_save(controller, container, item):
            status = 'Sent'
            additional_comments = 'N/A'
            subject = "Masters Store Order Multiple Change Request Notification"
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            domain_path = self.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            self.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

        self.events.scaffold_before_save += before_save
        self.events.scaffold_after_save += after_save
        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route_with(template='/multiple_changes/page/add')
    def add_form(self):
        self.meta.view.template_name = 'multiple_changes/form.html'

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Masters Store Order Multiple Change Request Form'
        self.context['user_fullname'] = self.session.get('user_fullname')

    def view(self, key):
        is_creator = False

        result = self.util.decode_key(key).get()

        if str(users.get_current_user()) == str(result.created_by):
            is_creator = True

        self.context['frmkey'] = self.request.params['frmkey']
        self.context['item'] = result
        self.context['requestor_name'] = result.requestor_name
        self.context['reason_for_change'] = result.reason_for_change
        self.context['dc_agreement'] = result.dc_agreement
        self.context['department_name'] = result.department_name
        self.context['supplier_site_number'] = result.supplier_site_number
        self.context['passed_business_rules'] = result.passed_business_rules
        self.context['submission_date'] = result.submission_date
        self.context['effective_date'] = result.effective_date
        self.context['supplier_name'] = result.supplier_name

        self.context['details'] = json.loads(result.details)

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by
        self.context['key'] = key

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Masters Store Order Multiple Change Request View'
        self.context['is_creator'] = is_creator

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

        item_number = self.request.get_all('item_number[]')
        item_description = self.request.get_all('item_description[]')
        indent_v_domestic = self.request.get_all('indent_v_domestic[]')
        old_som = self.request.get_all('old_som[]')
        new_som = self.request.get_all('new_som[]')
        buyer = self.request.get_all('buyer[]')
        sps = self.request.get_all('sps[]')
        outer_pack = self.request.get_all('outer_pack[]')
        ti = self.request.get_all('ti[]')
        hi = self.request.get_all('hi[]')
        weight = self.request.get_all('weight[]')
        order_point = self.request.get_all('order_point[]')
        pallet_quantity = self.request.get_all('pallet_quantity[]')
        comments = self.request.get_all('comments[]')

        details = []

        for count in range(len(item_number)):
            value_1 = Utils.html_escape(item_number[count])
            value_2 = Utils.html_escape(item_description[count])
            value_3 = indent_v_domestic[count]
            value_4 = old_som[count]
            value_5 = new_som[count]
            value_6 = Utils.html_escape(buyer[count])
            value_7 = Utils.html_escape(sps[count])
            value_8 = Utils.html_escape(outer_pack[count])
            value_9 = Utils.html_escape(ti[count])
            value_10 = Utils.html_escape(hi[count])
            value_11 = Utils.html_escape(weight[count])
            value_12 = Utils.html_escape(order_point[count])
            value_13 = Utils.html_escape(pallet_quantity[count])
            value_14 = Utils.html_escape(comments[count])

            if (value_1 != "" or value_2 != "" or value_3 != "" or value_4 != "" or value_5 != "" or value_6 != "" or value_7 != "" or
                    value_8 != "" or value_9 != "" or value_10 != "" or value_11 != "" or value_12 != "" or value_13 != "" or value_14 != ""):

                data = {}
                data['item_number'] = value_1
                data['item_description'] = value_2
                data['indent_v_domestic'] = value_3
                data['old_som'] = value_4
                data['new_som'] = value_5
                data['buyer'] = value_6
                data['sps'] = value_7
                data['outer_pack'] = value_8
                data['ti'] = value_9
                data['hi'] = value_10
                data['weight'] = value_11
                data['order_point'] = value_12
                data['pallet_quantity'] = value_13
                data['comments'] = value_14

            details.append(data)

        item_data.details = json.dumps(details)

        item_data.requestor_name = form['requestor_name']
        item_data.reason_for_change = form['reason_for_change']
        item_data.dc_agreement = form['dc_agreement']
        item_data.department_name = form['department_name']
        item_data.supplier_site_number = form['supplier_site_number']
        item_data.passed_business_rules = form['passed_business_rules']
        item_data.submission_date = form['submission_date']
        item_data.supplier_name = form['supplier_name']
        item_data.effective_date = form['effective_date']
        item_data.status = int(form['status'])

        entity = item_data.put()

        # Send email after editing #
        status = 'Edited'
        additional_comments = 'N/A'
        subject = "Change in Masters Store Order Multiple Change Request Notification"
        to = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
        domain_path = self.session.get('DOMAIN_PATH')

        item = entity.get()
        encoded_param = "?key=" + frmkey

        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'tempapprove')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'reject_level_1')

        self.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

        # return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))
        return self.redirect(self.uri(action='list', key=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']
        self.context['details'] = json.loads(item.details)
        self.context['key'] = key

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route_with(template='/multiple_changes/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.status)

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
            order = self.request.get('order_by_created') == 'desc' and MultipleChange.created_by or -MultipleChange.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and MultipleChange.status or -MultipleChange.status
        else:
            order = self.request.get('order_by_date') == 'desc' and MultipleChange.created or -MultipleChange.created

        if showAll:
            self.context['multiple_changes'] = MultipleChange.query().order(order)
        else:
            self.context['multiple_changes'] = MultipleChange.query(MultipleChange.created_by == users.get_current_user()).order(order)

        self.context['PAGE_TITLE'] = 'Masters Store Order Multiple Change Request List'
        self.context['isManager'] = self.context.get('user_isManager')
        self.context['sv_multiple_changes'] = self.context['multiple_changes']

    @route_with(template='/multiple_changes/remote_process/<entity_key>/<form_key>/<flag>')
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
            subject = "Masters Store Order Multiple Change Request Approval Notification"
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
                    subject = "Masters Store Order Multiple Change Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'
                elif flag == 'reject_level_2' and item.status == 2:
                    status = 4
                    exp_current_status = 2
                    subject = "Masters Store Order Multiple Change Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'

                # return 'item.status: %s || exp_current_status: %s || flag: %s' % (item.status, exp_current_status, flag)

                if item.status == exp_current_status:
                    item.status = status
                    item.put()

                    # Send Email
                    if flag == 'reject_level_1' or flag == 'reject_level_2' or flag == 'approve':
                        to = str(item.created_by)
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, encoded_param)
                    elif flag == 'tempapprove':
                        to = Users.get_user_list_by_group(entity.second_level_manager.get().key.urlsafe())
                        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'approve')
                        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'reject_level_2')

                        # Send an email to the 2nd Level Approver
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

                        # Send an email to the submitter
                        to = str(item.created_by)
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, encoded_param)
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
        subject = "Masters Store Order Multiple Change Request Approval Notification"

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        if (action == "tempapprove"):
            tab = '2'
            result.status = 2
            result.put()
            form_status = "Temporarily Approved"
            to = Users.get_user_list_by_group(self.context.get('second_group_approver').key.urlsafe())

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, keyid, form_key, 'reject_level_2')

            # Send an email to the 2nd Level Approver
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

            # Send an email to the submitter
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)
        elif (action == "approve"):
            tab = '3'
            result.status = 3
            result.put()
            form_status = "Approved"
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)
        elif (action == "reject"):
            tab = '4'
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Masters Store Order Multiple Change Request Rejection Notification"
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)

        if tab is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @classmethod
    def sendMail(self, form_status, resource, additional_comments, to, subject, domain_path, encoded_param, approve_link='#', reject_link='#'):

        items = ""
        details = resource.details
        requestor_name = resource.requestor_name
        reason_for_change = resource.reason_for_change
        dc_agreement = resource.dc_agreement
        department_name = resource.department_name
        supplier_site_number = resource.supplier_site_number
        passed_business_rules = resource.passed_business_rules
        submission_date = resource.submission_date
        effective_date = resource.effective_date
        supplier_name = resource.supplier_name
        date_time = Utils.localize_datetime(datetime.datetime.now())

        user = str(users.get_current_user())

        if details is not None:
            objLoad = json.loads(details)

            #logging.info(objLoad)

            for detail in objLoad:
                items += """\
                        Item Number - %s <br>
                        Item Description - %s <br>
                        Indent V Domestic - %s <br>
                        Old SOM - %s <br>
                        New SOM - %s <br>
                        Buyer - %s <br>
                        SPS - %s <br>
                        Outer Pack - %s <br>
                        TI - %s <br>
                        HI - %s <br>
                        Weight - %s <br>
                        Order Point - %s <br>
                        Pallet Quantity - %s <br>
                        Comments/Justification - %s <br><br>
                        """ % (detail['item_number'], detail['item_description'], detail['indent_v_domestic'], detail['old_som'],
                            detail['new_som'], detail['buyer'], detail['sps'], detail['outer_pack'],
                            detail['ti'], detail['hi'], detail['weight'], detail['order_point'],
                            detail['pallet_quantity'], detail['comments'])

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
                            <p>Hi, <br/><br/><br/>The request for masters store owner multiple change has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requestor Name</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

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

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">DC Agreement</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Department Name</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Supplier Site Number</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Passed Business Rules</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Approver's Comments</span><br/>
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
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/multiple_changes%s'>http://%s/multiple_changes%s</a>
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
                   """ % (form_status, date_time, user, requestor_name, reason_for_change, dc_agreement,
                            department_name, supplier_site_number, passed_business_rules, submission_date,
                            effective_date, supplier_name, items, additional_comments,
                            approve_reject_body,
                            domain_path, encoded_param, domain_path, encoded_param)

        mail.send(to, subject, msg_body, user)

    @route
    def export(self, key):
        self.response.headers['Content-Type'] = "application/vnd.ms-excel"
        result = self.util.decode_key(key).get()

        items = ""
        details = result.details
        requestor_name = result.requestor_name
        reason_for_change = result.reason_for_change
        dc_agreement = result.dc_agreement
        department_name = result.department_name
        supplier_site_number = result.supplier_site_number
        passed_business_rules = result.passed_business_rules
        submission_date = result.submission_date
        effective_date = result.effective_date
        supplier_name = result.supplier_name

        if details is not None:
            objLoad = json.loads(details)

            #logging.info(objLoad)

            for detail in objLoad:
                items += """\
                        Item Number - %s <br>
                        Item Description - %s <br>
                        Indent V Domestic - %s <br>
                        Old SOM - %s <br>
                        New SOM - %s <br>
                        Buyer - %s <br>
                        SPS - %s <br>
                        Outer Pack - %s <br>
                        TI - %s <br>
                        HI - %s <br>
                        Weight - %s <br>
                        Order Point - %s <br>
                        Pallet Quantity - %s <br>
                        Comments/Justification - %s <br><br>
                        """ % (detail['item_number'], detail['item_description'], detail['indent_v_domestic'], detail['old_som'],
                            detail['new_som'], detail['buyer'], detail['sps'], detail['outer_pack'],
                            detail['ti'], detail['hi'], detail['weight'], detail['order_point'],
                            detail['pallet_quantity'], detail['comments'])

        table = """\
                    <table border="1">
                        <thead>
                            <tr>
                                <th>Requestor Name:</th>
                                <th>Reason for Change:</th>
                                <th>DC Agreement:</td>
                                <th>Department Name:</td>
                                <th>Supplier Site Number:</th>
                                <th>Passed Business Rules:</th>
                                <th>Submission Date:</th>
                                <th>Effective Date:</th>
                                <th>Supplier Name:</th>
                                <th>Details:</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top">%s</td>
                                <td valign="top" colspan="1">%s</td>
                            </tr>
                        </tbody>
                    </table>
                   """ % (requestor_name, reason_for_change, dc_agreement,
                        department_name, supplier_site_number, passed_business_rules, submission_date,
                        effective_date, supplier_name, items)

        return table
