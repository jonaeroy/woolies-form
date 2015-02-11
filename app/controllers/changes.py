from ferris import Controller, scaffold, route
from ferris.core import mail
from google.appengine.api import users
from ..models.change import Change
from mains import Mains

import logging


class Changes(Controller):

    class Meta:
        prefix = ('api')
        components = (scaffold.Scaffolding,)

    class Scaffold:
        display_properties = ('created_by', 'created', 'Buyer_or_BAA_Name', 'Effective_Date','Merchandise_Manager','Submission_Date','Comments')

    edit = scaffold.edit
    delete = scaffold.delete

    @route
    def costchangeform(self):
        pass

    @route
    def list(self):

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and Change.created_by or -Change.created_by
        elif self.request.get('order_by_date'):
            order = self.request.get('order_by_status') == 'desc' and Change.Status or -Change.Status
        else:
            order = self.request.get('order_by_date') == 'desc' and Change.created or -Change.created

        if showAll:
            self.context['changes'] = Change.query().order(order)
        else:
            self.context['changes'] = Change.query(Change.created_by == users.get_current_user()).order(order)

    def add(self):
        return scaffold.add(self)

    def view(self, key):

        change = self.util.decode_key(key).get()
        self.context['buyer'] = change.Buyer_or_BAA_Name
        self.context['dept'] = change.Department
        self.context['effDate'] = change.Effective_Date
        self.context['subDate'] = change.Submission_Date
        self.context['comments'] = change.Comments
        self.context['merchMngr'] = change.Merchandise_Manager
        statusVar = change.Status
        self.context['status'] = Changes.convertStatus(statusVar)

    @classmethod
    def convertStatus(self, svar):

        if(svar == 1):
            convStat = "Pending Approval"
        elif(svar == 2):
            convStat = "Temporarily Approved"
        elif(svar == 3):
            convStat = "Approved"
        elif(svar == 4):
            convStat = "Rejected"
        else:
            convStat = "No Action Required"

        return convStat

    @route
    def sendNotif(self):

        form = self.request.params

        action = form['action']
        buyer = form['buyer']
        dept = form['dept']
        effDate = form['effdate']
        subDate = form['subdate']
        comments = form['comments']
        status = form['status']
        additional_comments = form['addcomments']

        keyid = form['keyid']
        change = self.util.decode_key(keyid).get()

        # Merchandise Manager
        to = form['to']

        if (comments == "" or comments is None):
            comments = "None"

        if (additional_comments == "" or additional_comments is None):
            additional_comments = "None"

        # For Merchandise Manager Approval
        if (action == "tempapprove"):

            change.Status = 2
            change.put()
            status = "Temporarily Approved"
            subject = "Woolies:Cost Change Approval Notification"
            Changes.sendMail(status,buyer,dept,effDate,subDate,comments,status,additional_comments,to,subject)

            # For Merchandise Manager and Merchandise Team Rejection
        elif (action == "reject"):
            change.Status = 4
            change.put()
            status = "Rejected"
            subject = "Woolies:Cost Change Rejection Notification"
            Changes.sendMail(status,buyer,dept,effDate,subDate,comments,status,additional_comments,to,subject)

        return self.redirect(self.uri(handler='changes', action='list'))

    @classmethod
    def sendMail(self,bstat,buyer,dept,effDate,subDate,comments,status,additional_comments,to,subject):

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
                                <p>Hi, <br/><br/><br/>The request for cost change has been <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                        </tr>
                        <!-- opening -->

                        <!-- 1 liner tall row important -->
                        <tr>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Buyer or BAA Name</span><br/>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Submission Date</span>
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
                                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Comments from Merchandise Manager</span><br/>
                                <p style="color: #262626; font-size: 12px;">%s</p>
                            </td>
                            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        </tr>
                        <!-- 1 row 2 liner -->

                        <!-- Footer -->
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
        """ % (bstat,buyer,dept,effDate,subDate,comments,status,additional_comments)

        mail.send(to, subject, msg_body, str(users.get_current_user()))
