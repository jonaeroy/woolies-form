from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from google.appengine.api import users
from ferris.core import mail
from ..controllers.users import Users
from ..models.logistltinotif import Logistltinotif
import logging
import urllib2
from app.component.drafts import Drafts

class Logistltinotifs(Controller):

    class Meta:
        prefix = ('admin',)
        components = (scaffold.Scaffolding,Pagination,Drafts)
        pagination_limit = 10
        action_form = 'ltinotificationform'

    class Scaffold:
        display_properties = ('created_by', 'created', 'Subject', 
            'Site','Pulse_Event_Number','Date_of_Incident','Date_unfit_certificate_issued',
            'Brief_description_of_incident','Care_provided_and_status_of_worker','Consideration_for_other_sites',
            'Any_additional_information','Person_leading_investigation_and_contact_details')

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200
        
    @route
    def ltinotificationform(self):

        tokey = self.context.get('first_group_approver').key.urlsafe()
        self.context['to']  = Users.get_user_list_by_group(tokey)

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def add(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = self.request.params
            user_email = self.session.get('user_email')
            domainpath = self.session.get('DOMAIN_PATH')
            tokey = self.context.get('first_group_approver').key.urlsafe()
            to = Users.get_user_list_by_group(tokey)

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            Logistltinotifs.sendNotif(form,to,user_email, domainpath, encoded_param)

        self.events.scaffold_after_save += after_save
        self.context['user'] = self.session.get('user_email')
        scaffold.add(self)

        return self.redirect(self.uri(action='list', key=form_key))

    @route
    def edit_data(self):

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

        form = self.request.params
        key = form['key']
        frmkey = form['frmkey']
        item_data = self.util.decode_key(key).get()

        item_data.To = form['To']
        item_data.CC = form['CC']
        item_data.Subject = form['Subject']

        item_data.Site = form['Site']
        item_data.Pulse_Event_Number = form['Pulse_Event_Number']
        item_data.Date_of_Incident = form['Date_of_Incident']
        item_data.Date_unfit_certificate_issued = form['Date_unfit_certificate_issued']
        item_data.Brief_description_of_incident = form['Brief_description_of_incident']
        item_data.Care_provided_and_status_of_worker = form['Care_provided_and_status_of_worker']
        item_data.Consideration_for_other_sites = form['Consideration_for_other_sites']
        item_data.Any_additional_information = form['Any_additional_information']
        item_data.Person_leading_investigation_and_contact_details = form['Person_leading_investigation_and_contact_details']
        
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

    @route
    def list(self):

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))

        frmkey = self.request.params['key']
        self.context['frmkey'] = frmkey

        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Logistltinotif.created_by or -Logistltinotif.created_by
        elif self.request.get('order_by_status')    :        
            order = self.request.get('order_by_status') == 'desc'  and Logistltinotif.Status or -Logistltinotif.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Logistltinotif.created or -Logistltinotif.created

        if showAll:
            self.context['logistltinotifs'] = Logistltinotif.query().order(order)
        else:
            self.context['logistltinotifs'] = Logistltinotif.query(Logistltinotif.created_by == users.get_current_user()).order(order)

        if not self.context['logistltinotifs'].fetch():

            return self.redirect(self.uri(action='ltinotificationform', key=frmkey))

    def view(self,key):

        logistltinotif = self.util.decode_key(key).get()
        self.context['logistltinotif'] = logistltinotif
        self.context['frmkey'] = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotif(self,form,to,user_email, domain_path, encoded_param):

        domain_path = str(domain_path)

        dateSent  = form['dateSent']
        To  = to
        CC = form['CC']
        if CC is None or str(CC) == "":
            CC = None
        Subject  = form['Subject']
        Site = form['Site']
        Pulse_Event_Number = form['Pulse_Event_Number']
        Date_of_Incident = form['Date_of_Incident']
        Date_unfit_certificate_issued = form['Date_unfit_certificate_issued']
        Brief_description_of_incident = form['Brief_description_of_incident']
        Care_provided_and_status_of_worker  = form['Care_provided_and_status_of_worker']
        Consideration_for_other_sites  = form['Consideration_for_other_sites']
        Any_additional_information  = form['Any_additional_information']
        Person_leading_investigation_and_contact_details  = form['Person_leading_investigation_and_contact_details']

        Logistltinotifs.sendMail(dateSent,To,CC,user_email,Subject,Site,Pulse_Event_Number,Date_of_Incident,
            Date_unfit_certificate_issued,Brief_description_of_incident,Care_provided_and_status_of_worker,
            Consideration_for_other_sites,Any_additional_information,
            Person_leading_investigation_and_contact_details,domain_path,encoded_param)

    @classmethod
    def sendMail(self,dateSent,To,CC,user_email,Subject,Site,Pulse_Event_Number,Date_of_Incident,
            Date_unfit_certificate_issued,Brief_description_of_incident,Care_provided_and_status_of_worker,
            Consideration_for_other_sites,Any_additional_information,
            Person_leading_investigation_and_contact_details,domain_path,encoded_param):

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
                            <p>Hi, <br/><br/><br/>Loss time inquiry form for logistics has been logged with the following details</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Submitted By</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

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

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Site</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Pulse Event Number</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date of Incident</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date unfit certificate issued</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Brief description of incident</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Care provided and status of worker</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 liner tall row important -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Consideration for other sites</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- 1 row 2 liner -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Any additional information</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

                    <!-- 1 row 2 liner -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Person leading investigation and contact details</span><br/>
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
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/logistltinotifs%s'>http://%s/logistltinotifs%s</a>
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
        """ % (user_email,Subject,Site,Pulse_Event_Number ,Date_of_Incident ,Date_unfit_certificate_issued ,
            Brief_description_of_incident ,Care_provided_and_status_of_worker ,Consideration_for_other_sites ,
            Any_additional_information ,Person_leading_investigation_and_contact_details,
            domain_path, encoded_param, domain_path, encoded_param)

        if CC is None:
            mail.send(To, Subject, msg_body, str(user_email))
        else:
            mail.send(To, Subject, msg_body, str(user_email),cc=CC)
