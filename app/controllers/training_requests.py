from ferris import Controller, scaffold, route_with, route
from google.appengine.api import users
from ferris.components.pagination import Pagination
from ferris.core import mail
from ..models.training_request import TrainingRequest
from ..controllers.utils import Utils
from ..controllers.users import Users
import logging
# import json
import datetime
import urllib2
from app.component.drafts import Drafts


class TrainingRequests(Controller):

    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination,Drafts)
        pagination_limit = 10

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

    @route_with(template='/training/page/add')
    def form_add(self):
        self.meta.view.template_name = 'training_requests/form.html'

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Training Request Form'
        self.context['user_fullname'] = self.session.get('user_fullname')
        self.context['current_user'] = users.get_current_user()

    def add(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            status = 'Sent'
            additional_comments = 'N/A'
            subject = "Training Request Notification"
            to = Users.get_user_list_by_group(controller.context.get('first_group_approver').key.urlsafe())
            domain_path = self.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            TrainingRequests.sendMail(status, item, additional_comments, to, subject, domain_path, encoded_param)

        self.events.scaffold_after_save += after_save
        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route
    def list(self):
        usertypekey = self.session.get('user_groups')

        if usertypekey is None:
            usertype = None
        else:
            usertype = self.util.decode_key(usertypekey.urlsafe()).get()

        self.context['usertype'] = usertype
        form_key = self.session.get(self.name + "_KEY")
        self.context['frmkey'] = form_key

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and TrainingRequest.created_by or -TrainingRequest.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and TrainingRequest.status or -TrainingRequest.status
        else:
            order = self.request.get('order_by_date') == 'desc' and TrainingRequest.created or -TrainingRequest.created

        if showAll:
            self.context['training_requests'] = TrainingRequest.query().order(order)
        else:
            self.context['training_requests'] = TrainingRequest.query(TrainingRequest.created_by == users.get_current_user()).order(order)

        if not self.context['training_requests'].fetch():
            return self.redirect(self.uri(action='form_add', key=form_key))

        self.context['PAGE_TITLE'] = 'Training Request List'
        self.context['isManager'] = self.context.get('user_isManager');

    @route
    def edit_data(self):

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

        form = self.request.params
        key = form['key']
        frmkey = form['frmkey']
        item_data = self.util.decode_key(key).get()

        item_data.to = form['to']
        item_data.employee_number = form['employee_number']
        item_data.email_address = form['email_address']
        item_data.participant_name = form['participant_name']
        item_data.preferred_training_day = form['preferred_training_day']
        item_data.participant_position_title = form['participant_position_title']
        item_data.shift_type = form['shift_type']
        item_data.participant_dob = form['participant_dob']
        item_data.preferred_training_location = form['preferred_training_location']
        item_data.cost_center_number = form['cost_center_number']
        item_data.current_cert_exp_date = form['current_cert_exp_date']
        item_data.participant_mobile_number = form['participant_mobile_number']
        item_data.store_site_name = form['store_site_name']
        item_data.division = form['division']
        item_data.first_aid = form['first_aid']
        item_data.responsible_service_of_alcohol = form['responsible_service_of_alcohol']
        item_data.fire_training = form['fire_training']
        item_data.fork_lift = form['fork_lift']
        item_data.rehabilitation = form['rehabilitation']
        item_data.food_safety = form['food_safety']
        item_data.safety = form['safety']
        item_data.special_instructions = form['special_instructions']
        item_data.status = int(form['status'])

        item_data.put()

        return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self, key):
        result = self.util.decode_key(key).get()

        self.context['item'] = result
        self.context['to'] = result.to
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['employee_number'] = result.employee_number
        self.context['email_address'] = result.email_address
        self.context['participant_name'] = result.participant_name
        self.context['preferred_training_day'] = result.preferred_training_day
        self.context['participant_position_title'] = result.participant_position_title
        self.context['shift_type'] = result.shift_type
        self.context['participant_dob'] = result.participant_dob
        self.context['preferred_training_location'] = result.preferred_training_location
        self.context['cost_center_number'] = result.cost_center_number
        self.context['current_cert_exp_date'] = result.current_cert_exp_date
        self.context['participant_mobile_number'] = result.participant_mobile_number
        self.context['store_site_name'] = result.store_site_name
        self.context['division'] = result.division
        self.context['first_aid'] = result.first_aid
        self.context['responsible_service_of_alcohol'] = result.responsible_service_of_alcohol
        self.context['fire_training'] = result.fire_training
        self.context['fork_lift'] = result.fork_lift
        self.context['rehabilitation'] = result.rehabilitation
        self.context['food_safety'] = result.food_safety
        self.context['safety'] = result.safety
        self.context['special_instructions'] = result.special_instructions

        self.context['modified'] = result.modified
        self.context['modified_by'] = result.modified_by
        self.context['key'] = key

        statusVar = result.status

        self.context['status'] = Utils.convertStatus(statusVar)

        for key, value in self.session.items():
            self.context[key] = value

        self.context['PAGE_TITLE'] = 'Training Request View'

    @route
    def delete(self, key):
        result = self.util.decode_key(key).get()
        result.key.delete()
        return self.redirect(self.uri(action='delete_suc'))

    @route
    def delete_suc(self):
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def sendNotif(self):

        form = self.request.params

        action = form['action']
        additional_comments = form['additional_comments']
        keyid = form['keyid']

        result = self.util.decode_key(keyid).get()
        domain_path = self.session.get('DOMAIN_PATH')
        subject = "Training Request Approval Notification"

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        if (action == "tempapprove"):
            result.status = 2
            result.put()
            form_status = "Temporarily Approved"
            to = Users.get_user_list_by_group(self.context.get('second_group_approver').key.urlsafe())
            TrainingRequests.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)
        elif (action == "approve"):
            result.status = 3
            result.put()
            form_status = "Approved"
            to = str(result.created_by)  # temporary recipient
            TrainingRequests.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)
        elif (action == "reject"):
            result.status = 4
            result.put()
            form_status = "Rejected"
            subject = "Training Request Rejection Notification"
            to = str(result.created_by)
            TrainingRequests.sendMail(form_status, result, additional_comments, to, subject, domain_path, encoded_param)

        return self.redirect(self.uri(action='list'))

    @classmethod
    def sendMail(self, form_status, resource, additional_comments, to, subject, domain_path, encoded_param):

        to = resource.to
        employee_number = resource.employee_number
        email_address = resource.email_address
        participant_name = resource.participant_name
        preferred_training_day = resource.preferred_training_day
        participant_position_title = resource.participant_position_title
        shift_type = resource.shift_type
        participant_dob = resource.participant_dob
        preferred_training_location = resource.preferred_training_location
        cost_center_number = resource.cost_center_number
        current_cert_exp_date = resource.current_cert_exp_date
        participant_mobile_number = resource.participant_mobile_number
        store_site_name = resource.store_site_name
        division = resource.division
        first_aid = resource.first_aid
        responsible_service_of_alcohol = resource.responsible_service_of_alcohol
        fire_training = resource.fire_training
        fork_lift = resource.fork_lift
        rehabilitation = resource.rehabilitation
        food_safety = resource.food_safety
        safety = resource.safety
        special_instructions = resource.special_instructions
        date_time = Utils.localize_datetime(datetime.datetime.now())

        user = str(users.get_current_user())

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
                        <p>Hi, <br/><br/><br/>The request for training has been <span style="color: #ff502d"><strong>%s</strong></span> on <span style="color: #ff502d"><strong>%s</strong></span> by <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

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

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Employee Number</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Participant's Email Address</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Participant Name</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Preferred Training Day</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Participant Position Title</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Shift Type</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Participant D.O.B</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Preferred Training Location</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Cost Center Number</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Current Certificate Expiry Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Participant Mobile Number</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store/Site Name</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Division</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">Training Requirement</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">First Aid</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Responsible Service of Alcohol</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Fire Training</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Fork Lift</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Rehabilitation and Return to Work Coordinator</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Food Safety</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Safety</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Special Instructions</span><br/>
                        <p style="color: #262626; font-size: 12px;">%s</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 row 2 liner -->

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


                <!-- Footer -->
                 <tr>
                    <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                    <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                        <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/training_requests%s'>http://%s/training_requests%s</a>
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
                   """ % (form_status, date_time, user, to, employee_number, email_address, participant_name,
                        preferred_training_day, participant_position_title, shift_type, participant_dob,
                        preferred_training_location, cost_center_number, current_cert_exp_date, participant_mobile_number,
                        store_site_name, division, first_aid, responsible_service_of_alcohol, fire_training,
                        fork_lift, rehabilitation, food_safety, safety,
                        special_instructions, additional_comments, domain_path, encoded_param, domain_path, encoded_param)

        mail.send(to, subject, msg_body, user)

    @route
    def export(self, key):
        self.response.headers['Content-Type'] = "application/vnd.ms-excel"
        result = self.util.decode_key(key).get()

        to = result.to
        employee_number = result.employee_number
        email_address = result.email_address
        participant_name = result.participant_name
        preferred_training_day = result.preferred_training_day
        participant_position_title = result.participant_position_title
        shift_type = result.shift_type
        participant_dob = result.participant_dob
        preferred_training_location = result.preferred_training_location
        cost_center_number = result.cost_center_number
        current_cert_exp_date = result.current_cert_exp_date
        participant_mobile_number = result.participant_mobile_number
        store_site_name = result.store_site_name
        division = result.division
        first_aid = result.first_aid
        responsible_service_of_alcohol = result.responsible_service_of_alcohol
        fire_training = result.fire_training
        fork_lift = result.fork_lift
        rehabilitation = result.rehabilitation
        food_safety = result.food_safety
        safety = result.safety
        special_instructions = result.special_instructions

        table = """\
                <table border="1">
                    <thead>
                        <tr>
                            <th>To</th>
                            <th>Employee No</th>
                            <th>Name</th>
                            <th>Division</th>
                            <th>Position Title</th>
                            <th>D.O.B</th>
                            <th>Store/Site Name</th>
                            <th>Cost Centre</th>
                            <th>Phone No</th>
                            <th>Email</th>
                            <th>Preferred Training Day</th>
                            <th>Shift Type</th>
                            <th>Preferred Training Location</th>
                            <th>Current Certificate Expiry Date</th>
                            <th>First Aid</th>
                            <th>Forklift</th>
                            <th>Responsible Service of Alcohol</th>
                            <th>Rehabilitation and Return to Work Coordinator</th>
                            <th>Fire Training</th>
                            <th>Food Safety</th>
                            <th>Safety</th>
                            <th>Special Instructions</th>
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
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                            <td valign="top">%s</td>
                        </tr>
                    </tbody>
                </table>
               """ % (to, employee_number, participant_name, division,
                    participant_position_title, participant_dob, store_site_name, cost_center_number,
                    participant_mobile_number, email_address, preferred_training_day, shift_type,
                    preferred_training_location, current_cert_exp_date, first_aid, fork_lift, responsible_service_of_alcohol,
                    rehabilitation, fire_training, food_safety, safety, special_instructions)

        return table
