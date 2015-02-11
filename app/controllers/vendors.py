from ferris import Controller, scaffold, route_with, route
from google.appengine.api import users
from ferris.core import mail
from ..models.dc import Dc
from ferris.components import search, pagination
from ..controllers.utils import Utils
from ..controllers.users import Users
from ..models.vendor import Vendor
from ..models.vendor_list import VendorList
from ferris.components.upload import Upload
import datetime
import logging
import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView
from google.appengine.ext import blobstore

from ferris.core.ndb import ndb

class Vendors(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, SplitView, pagination.Pagination, Upload, Drafts, SplitView)
        pagination_limit = 10
        sv_result_variable = 'vendors'
        sv_status_field = 'status'
        action_form = 'add_form'

    class Scaffold:
        display_properties = ('status', 'created_by', 'created')

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

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

    @route_with(template='/vendors/page/add')
    def add_form(self):
        form_key = self.context.get('form_key')

        def before_save(controller, container, item):
            if item.issue_raised_in_pct == '':
                item.issue_raised_in_pct = 'No'

        def after_save(controller, container, item):
            status = 'Sent'
            additional_comments = 'N/A'
            subject = "Vendor Capability Notification"
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            domain_path = self.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            # Send an email to the 1st Level Approver
            self.sendMail(status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

            # Send an email to the CC'd address
            to = item.to
            cc = item.cc

            self.sendMail(status, item, additional_comments, to, subject, domain_path, cc, encoded_param)

        self.events.scaffold_before_save += before_save
        self.events.scaffold_after_save += after_save
        dcs = Dc.get_dcs()
        vendors = VendorList.get_all()

        self.context['dcs'] = dcs
        self.context['vendors'] = vendors
        self.meta.view.template_name = 'vendors/form.html'
        self.context['PAGE_TITLE'] = 'Vendor Capability Form'

        self.scaffold.redirect = '/vendors?key=' + form_key

        return scaffold.add(self)

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

        # show all queries if manager of the form
        showAll = self.context.get('user_isManager')

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and Vendor.created_by or -Vendor.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and Vendor.status or -Vendor.status
        else:
            order = self.request.get('order_by_date') == 'desc' and Vendor.created or -Vendor.created

        if showAll:
            self.context['vendors'] = Vendor.query().order(order)
        else:
            self.context['vendors'] = Vendor.query(Vendor.created_by == users.get_current_user()).order(order)

        self.context['PAGE_TITLE'] = 'Vendor Capability List'
        self.context['isManager'] = self.context.get('user_isManager');
        self.context['isFormAdmin'] = self.context.get('user_isFormAdmin');
        self.context['frmkey'] = self.session.get(self.name + "_KEY")

        self.context['sv_vendors'] = self.context['vendors']

    def view(self, key):

        is_creator = False

        result = self.util.decode_key(key).get()

        if str(users.get_current_user()) == str(result.created_by):
            is_creator = True

        self.context['subject'] = result.subject
        self.context['cc'] = result.cc
        self.context['to'] = result.to
        self.context['dc'] = result.dc
        self.context['po_number'] = result.po_number
        self.context['delivery_date'] = result.delivery_date
        self.context['vendor_number'] = result.vendor_number
        self.context['vendor_name'] = result.vendor_name
        self.context['pallets_received'] = result.pallets_received
        self.context['pallets_affected'] = result.pallets_affected
        self.context['po_rejected'] = result.po_rejected
        self.context['po_on_woolworths_primary_flight'] = result.po_on_woolworths_primary_flight
        self.context['issue_raised_in_pct'] = result.issue_raised_in_pct
        self.context['notes'] = result.notes

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)
        self.context['form_status'] = statusVar
        self.context['download_link'] = Utils.generate_download_link(result.attachment)

        self.context['PAGE_TITLE'] = 'Vendor Capability View'
        self.context['keyid'] = result.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['is_creator'] = is_creator

    @route_with(template='/vendors/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.status)

    @route
    def edit_locked(self):
        form_key = self.request.params['frmkey']
        self.context['key'] = form_key

    @route_with(template='/vendors/page/edit/<key>/<form_key>')
    def edit_data(self, key, form_key):
        item = self.util.decode_key(key).get()

        dcs = Dc.get_dcs()
        vendors = VendorList.get_all()

        attachment = None

        if item.attachment is not None:
            attachment = blobstore.BlobInfo.get(item.attachment)
            attachment = attachment.filename

        self.context['attachment'] = attachment
        self.context['dcs'] = dcs
        self.context['vendors'] = vendors
        self.context['item'] = item
        self.context['frmkey'] = form_key
        self.context['key'] = key

        self.meta.view.template_name = 'vendors/update.html'
        self.scaffold.redirect = '/vendors?key=' + form_key

        # Send email after editing #
        def after_save(controller, container, item):
            status = 'Edited'
            additional_comments = 'N/A'
            subject = "Change in Vendor Capability Request Notification"
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            domain_path = self.session.get('DOMAIN_PATH')

            encoded_param = "?key=" + form_key

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'tempapprove')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject_level_1')

            # Send an email to the 1st Level Approver
            self.sendMail(status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

            # Send an email to the CC'd address
            to = item.cc
            self.sendMail(status, item, additional_comments, to, subject, domain_path, None, encoded_param)

        self.events.scaffold_after_save += after_save

        return scaffold.edit(self, key)

    @route_with(template='/vendors/remote_process/<entity_key>/<form_key>/<flag>')
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
            subject = "Vendor Capability Request Approval Notification"
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
                    subject = "Vendor Capability Request Rejection Notification"
                    form_status = "Rejected"
                    tab = '4'
                elif flag == 'reject_level_2' and item.status == 2:
                    status = 4
                    exp_current_status = 2
                    subject = "Vendor Capability Request Rejection Notification"
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
                        to = str(item.created_by) + ";" + item.to
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, cc, encoded_param)
                    elif flag == 'tempapprove':
                        to = Users.get_user_list_by_group(entity.second_level_manager.get().key.urlsafe())
                        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'approve')
                        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, entity_key, form_key, 'reject_level_2')

                        # Send an email to the 2nd Level Approver
                        self.sendMail(form_status, item, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

                        # Send an email to the submitter
                        to = str(item.created_by) + ";" + item.to
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
        subject = "Vendor Capability Approval Notification"

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

            # Send an email to the 2nd Level Approver
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, None, encoded_param, approve_link, reject_link)

            # Send an email to the submitter and to the CC'd address
            to = str(result.created_by) + ";" + result.to
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "approve"):
            tab = '3'
            result.status = 3
            result.put()
            form_status = "Approved"
            to = str(result.created_by) + ";" + result.to
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)
        elif (action == "reject"):
            tab = '4'
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Vendor Capability Rejection Notification"
            to = str(result.created_by) + ";" + result.to
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, cc, encoded_param)

        if tab is None:
            return self.redirect(self.uri(action='list', key=form_key))
        else:
            return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @classmethod
    def sendMail(self, form_status, resource, additional_comments, to, subject, domain_path, cc, encoded_param, approve_link='#', reject_link='#'):

        user = str(users.get_current_user())

        if form_status != 'Edited':
            subject = resource.subject

        # resource_to = resource.to
        # resource_to = resource_to.split(';')
        # input_to = to.split(';')

        # mergedlist = resource_to + input_to
        # to = ';'.join(mergedlist)

        dc = resource.dc
        po_number = resource.po_number
        delivery_date = resource.delivery_date
        vendor_number = resource.vendor_number
        vendor_name = resource.vendor_name
        pallets_received = resource.pallets_received
        pallets_affected = resource.pallets_affected
        po_rejected = resource.po_rejected
        po_on_woolworths_primary_flight = resource.po_on_woolworths_primary_flight
        attachment = Utils.generate_download_link(resource.attachment)
        date_time = Utils.localize_datetime(datetime.datetime.now())
        body = ""

        try:
            issue_raised_in_pct = resource.issue_raised_in_pct
        except:
            issue_raised_in_pct = 'No'

        notes = resource.notes

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

        body = """\
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
                                <p>Hi, <br/><br/><br/>The request for vendors capability has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        </tr>
                        <!-- opening -->

                        <!-- 1 liner 2 columns -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">DC</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">PO Number</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Delivery Date</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Vendor Number</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Vendor Name</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pallets Received</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pallets Affected</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Was the PO rejected</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Was the PO on Woolworths Primary Flight</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Was this issue raise in the PCT</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Notes</span><br/>
                                <p style="color: #262626; font-size: 12px;">%s</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 row 2 liner -->

                        <!-- 1 row 2 liner -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Additional Comments</span><br/>
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

                        <!-- Buttons -->
                        %s
                        <!-- Buttons -->

                        <!-- Footer -->
                         <tr>
                            <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                            <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                                <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                                    <a style='color: #3b9ff3;' target='_blank' href='http://%s/vendors%s'>http://%s/vendors%s</a>
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
               """ % (form_status, date_time, user, dc, po_number, delivery_date, vendor_number, vendor_name,
                    pallets_received, pallets_affected, po_rejected,
                    po_on_woolworths_primary_flight, issue_raised_in_pct, notes, additional_comments, attachment,
                    approve_reject_body,
                    domain_path, encoded_param, domain_path, encoded_param)

        if str(cc) != "" and cc is not None:
            mail.send(to, subject, body, user, cc=cc)
        else:
            mail.send(to, subject, body, user)
