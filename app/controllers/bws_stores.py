from ferris import Controller, scaffold, route_with, route
from google.appengine.api import users
from ferris.core import mail
from ..models.bws_store import BwsStore
from ferris.components.pagination import Pagination
from ..controllers.utils import Utils
from ..controllers.users import Users
import json
import logging
import datetime
import urllib2
from app.component.drafts import Drafts
from app.component.split_view import SplitView

class BwsStores(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, SplitView, Pagination, Drafts)
        pagination_limit = 10
        sv_result_variable = 'bws_stores'
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

    @route_with(template='/bws/page/add')
    def add_form(self):
        trading_hours = json.dumps(['12:00', '12:30', '1:00', '1:30', '2:00', '2:30', '3:00', '3:30', '4:00', '4:30', '5:00', '5:30', '6:00', '6:30', '7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30'])
        trading_hours = json.loads(trading_hours)
        self.context['trading_hours'] = trading_hours
        self.meta.view.template_name = 'bws_stores/form.html'

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'BWS Store Information Form'

    def add(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            status = 'Sent'
            additional_comments = 'N/A'
            subject = 'BWS Store Information Request Notification'
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            domain_path = self.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key
            key = item.key.urlsafe()

            approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'approve')
            reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, form_key, 'reject')

            self.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

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

    @route
    def list(self):
        usertypekey = self.session.get('user_groups')

        if usertypekey is None:
            usertype = None
        else:
            usertype = self.util.decode_key(usertypekey.urlsafe()).get()

        self.context['usertype'] = usertype
        self.context['frmkey'] = self.request.params['key']

        try:
            self.context['tab'] = self.request.params['status']
        except:
            self.context['tab'] = None

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and BwsStore.created_by or -BwsStore.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and BwsStore.status or -BwsStore.status
        else:
            order = self.request.get('order_by_date') == 'desc' and BwsStore.created or -BwsStore.created

        if showAll:
            self.context['bws_stores'] = BwsStore.query().order(order)
        else:
            self.context['bws_stores'] = BwsStore.query(BwsStore.created_by == users.get_current_user()).order(order)

        self.context['PAGE_TITLE'] = 'BWS Store Information List'
        self.context['isManager'] = self.context.get('user_isManager')
        self.context['sv_bws_stores'] = self.context['bws_stores']

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

        item_data.new_changes_closures = form['new_changes_closures']
        item_data.store_number = form['store_number']
        item_data.store_name = form['store_name']
        item_data.effective_date = form['effective_date']
        item_data.state = form['state']
        item_data.banner = form['banner']
        item_data.area = form['area']
        item_data.address = form['address']
        item_data.phone_number = form['phone_number']
        item_data.fax_number = form['fax_number']
        item_data.manager_name = form['manager_name']
        item_data.status = int(form['status'])

        item_data.trading_hour_monday_open = form['trading_hour_monday_open']
        item_data.trading_hour_tuesday_open = form['trading_hour_tuesday_open']
        item_data.trading_hour_wednesday_open = form['trading_hour_wednesday_open']
        item_data.trading_hour_thursday_open = form['trading_hour_thursday_open']
        item_data.trading_hour_friday_open = form['trading_hour_friday_open']
        item_data.trading_hour_saturday_open = form['trading_hour_saturday_open']
        item_data.trading_hour_sunday_open = form['trading_hour_sunday_open']

        item_data.trading_hour_monday_close = form['trading_hour_monday_close']
        item_data.trading_hour_tuesday_close = form['trading_hour_tuesday_close']
        item_data.trading_hour_wednesday_close = form['trading_hour_wednesday_close']
        item_data.trading_hour_thursday_close = form['trading_hour_thursday_close']
        item_data.trading_hour_friday_close = form['trading_hour_friday_close']
        item_data.trading_hour_saturday_close = form['trading_hour_saturday_close']
        item_data.trading_hour_sunday_close = form['trading_hour_sunday_close']

        item_data.channel = form['channel']
        item_data.merch_state = form['merch_state']
        item_data.company = form['company']
        item_data.other = form['other']

        entity = item_data.put()

        # Send email after editing #
        status = 'Edited'
        additional_comments = 'N/A'
        subject = 'Change in BWS Store Information Request Notification'
        item = entity.get()
        to = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
        domain_path = self.session.get('DOMAIN_PATH')
        encoded_param = "?key=" + frmkey

        # Create approve/reject link
        approve_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'approve')
        reject_link = "http://%s/%s/remote_process/%s/%s/%s" % (domain_path, self.name, key, frmkey, 'reject')

        self.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param, approve_link, reject_link)

        # return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))
        return self.redirect(self.uri(action='list', key=frmkey))

    @route_with(template='/bws_stores/remote_process/<entity_key>/<form_key>/<flag>')
    def approve_reject_via_email(self, entity_key, form_key, flag):
        item = self.util.decode_key(entity_key).get()
        domain_path = self.session.get('DOMAIN_PATH')
        encoded_param = "?key=" + form_key
        additional_comments = 'N/A'

        if item:
            if flag == 'approve':
                status = 3
                subject = "BWS Store Information Request Approval Notification"
                form_status = "Approved"
                tab = '3'
            elif flag == 'reject' and item.status != 3:
                status = 4
                subject = "BWS Store Information Request Rejection Notification"
                form_status = "Rejected"
                tab = '4'

            # Also check if approver or not
            if item.status == 1:
                item.status = status
                item.put()

                # Send Email
                to = str(item.created_by)
                self.sendMail(form_status, item, additional_comments, to, subject, domain_path, encoded_param)

                # Redirect
                return self.redirect(self.uri(action='list', key=form_key, status=tab))
            else:
                return self.components.split_view.already_approved(form_key)
        else:
            return 404

    @route_with(template='/bws_stores/fetch_request_status/<key>')
    def fetch_status(self, key):
        result = self.util.decode_key(key).get()
        return str(result.status)

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']
        self.context['key'] = key

        trading_hours = json.dumps(['12:00', '12:30', '1:00', '1:30', '2:00', '2:30', '3:00', '3:30', '4:00', '4:30', '5:00', '5:30', '6:00', '6:30', '7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30'])
        trading_hours = json.loads(trading_hours)
        self.context['trading_hours'] = trading_hours

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
        self.context['new_changes_closures'] = str(result.new_changes_closures).upper()
        self.context['effective_date'] = result.effective_date
        self.context['store_number'] = result.store_number
        self.context['store_name'] = result.store_name
        self.context['state'] = result.state
        self.context['banner'] = result.banner
        self.context['area'] = result.area
        self.context['address'] = result.address
        self.context['phone_number'] = result.phone_number
        self.context['fax_number'] = result.fax_number
        self.context['manager_name'] = result.manager_name

        self.context['trading_hour_monday_open'] = result.trading_hour_monday_open
        self.context['trading_hour_tuesday_open'] = result.trading_hour_tuesday_open
        self.context['trading_hour_wednesday_open'] = result.trading_hour_wednesday_open
        self.context['trading_hour_thursday_open'] = result.trading_hour_thursday_open
        self.context['trading_hour_friday_open'] = result.trading_hour_friday_open
        self.context['trading_hour_saturday_open'] = result.trading_hour_saturday_open
        self.context['trading_hour_sunday_open'] = result.trading_hour_sunday_open

        self.context['trading_hour_monday_close'] = result.trading_hour_monday_close
        self.context['trading_hour_tuesday_close'] = result.trading_hour_tuesday_close
        self.context['trading_hour_wednesday_close'] = result.trading_hour_wednesday_close
        self.context['trading_hour_thursday_close'] = result.trading_hour_thursday_close
        self.context['trading_hour_friday_close'] = result.trading_hour_friday_close
        self.context['trading_hour_saturday_close'] = result.trading_hour_saturday_close
        self.context['trading_hour_sunday_close'] = result.trading_hour_sunday_close

        self.context['channel'] = result.channel
        self.context['merch_state'] = result.merch_state
        self.context['company'] = result.company

        self.context['other'] = result.other

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)
        self.context['domain_path'] = self.session.get('DOMAIN_PATH')
        self.context['is_creator'] = is_creator

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'BWS Store Information View'

        if self.context.get('frmkey') != "" or self.context.get('frmkey') is not None:
            self.context['form_key'] = "?key=" + self.context.get('frmkey')

    @route
    def sendNotif(self):
        form = self.request.params

        action = form['action']
        additional_comments = form['additional_comments']
        keyid = form['keyid']

        result = self.util.decode_key(keyid).get()
        domain_path = self.session.get('DOMAIN_PATH')
        subject = 'BWS Store Information Request Notification'

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        if (action == "forward"):
            tab = '3'
            result.status = 3
            result.put()
            form_status = "Approved"
            subject = "BWS Store Information Request Approval Notification"
            #to = Users.get_user_list_by_group(self.context.get('first_group_approver').key.urlsafe())
            to = str(result.created_by)
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)
        elif (action == "reject"):
            tab = '4'
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "BWS Store Information Request Rejection Notification"
            to = str(result.created_by)  # Sent to the one who accomplished the form
            self.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)

        return self.redirect(self.uri(action='list', key=form_key, status=tab))

    @classmethod
    def sendMail(self, status, result, additional_comments, to, subject, domain_path, encoded_param, approve_link='#', reject_link='#'):

        user = str(users.get_current_user())
        domain_path = str(domain_path)

        new_changes_closures = str(result.new_changes_closures).upper()
        effective_date = result.effective_date
        store_number = result.store_number
        store_name = result.store_name
        state = result.state
        banner = result.banner
        area = result.area
        address = result.address
        phone_number = result.phone_number
        fax_number = result.fax_number
        manager_name = result.manager_name
        trading_hour_monday_open = result.trading_hour_monday_open
        trading_hour_monday_close = result.trading_hour_monday_close
        trading_hour_tuesday_open = result.trading_hour_tuesday_open
        trading_hour_tuesday_close = result.trading_hour_tuesday_close
        trading_hour_wednesday_open = result.trading_hour_wednesday_open
        trading_hour_wednesday_close = result.trading_hour_wednesday_close
        trading_hour_thursday_open = result.trading_hour_thursday_open
        trading_hour_thursday_close = result.trading_hour_thursday_close
        trading_hour_friday_open = result.trading_hour_friday_open
        trading_hour_friday_close = result.trading_hour_friday_close
        trading_hour_saturday_open = result.trading_hour_saturday_open
        trading_hour_saturday_close = result.trading_hour_saturday_close
        trading_hour_sunday_open = result.trading_hour_sunday_open
        trading_hour_sunday_close = result.trading_hour_sunday_close
        channel = result.channel
        merch_state = result.merch_state
        company = result.company
        other = result.other

        date_time = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

        approve_reject_body = '<!-- No Buttons -->'

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

        body = """\
                <html>
                <body>

                <span style="width: 600px; padding: 1px; background: #d3d3d3; display: block;">
                <table style="padding: 0; margin: 0; width:600px; font-family:Arial,Helvetica,sans-serif; font-size: 12px; letter-spacing: 1px; border-spacing: 0; background-color: #fff; color: #7d7d7d;" border="0">
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
                                <p>Hi, <br/><br/><br/>The request for BWS has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        </tr>
                        <!-- opening -->

                        <!-- Items and Date -->
                        <tr style="">
                            <td style="padding-top: 40px; margin: 0; width: 50px;">&nbsp;</td>
                            <td style="padding: 40px 0 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="color: #b85e80; font-weight: bold;">%s</span>
                            </td>
                            <td style="padding: 40px 0 20px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                            </td>
                            <td style="padding: 40px 0 20px 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- Items and Date -->

                        <!-- 1 liner 2 columns -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Effective Date:</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Number</span>
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
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Name</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner 2 columns -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">State</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Banner</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Area</span>
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
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Address</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner 2 columns -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Phone Number</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Fax Number</span>
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
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Manager's Name</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 10px 0; margin: 0; width: 500px; border-bottom: 1px solid #d8dee3;">
                                <p><span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Trading Hours</span></p>
                                    <table style="border-spacing: 0;">
                                    <thead>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; background: #2c3742; padding: 5px; color: #fff;">Day</td>
                                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Open</td>
                                            <td style="font-weight: bold; background: #2c3742; color: #fff; padding: 5px;">Close</td>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Monday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Tuesday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Wednesday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Thursday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Friday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Saturday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                        <tr>
                                            <td style="font-weight: bold; width: 130px; padding: 5px;">Sunday</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                            <td style="padding: 5px; text-align: center;">%s</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Channel</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Merch State</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Company</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                       <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Other</span><br/>
                                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 liner tall row important -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Additional Comments</span><br/>
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
                                    <a href='http://%s/bws_stores%s'>http://%s/bws_stores%s</a>
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
                   """ % (status, date_time, user, new_changes_closures, effective_date, store_number, store_name, state, banner, area, address, phone_number, fax_number, manager_name,
                          trading_hour_monday_open, trading_hour_monday_close, trading_hour_tuesday_open, trading_hour_tuesday_close,
                          trading_hour_wednesday_open, trading_hour_wednesday_close, trading_hour_thursday_open, trading_hour_thursday_close,
                          trading_hour_friday_open, trading_hour_friday_close, trading_hour_saturday_open, trading_hour_saturday_close,
                          trading_hour_sunday_open, trading_hour_sunday_close, channel, merch_state, company, other, additional_comments,
                          approve_reject_body,
                          domain_path, encoded_param, domain_path, encoded_param)

        mail.send(to, subject, body, user)
