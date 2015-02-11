from ferris import Controller, scaffold, route
from ..models.datarequest import Datarequest
from google.appengine.api import users
from ferris.core import mail
from ..controllers.utils import Utils
from app.component.drafts import Drafts
class Datarequests(Controller):

    class Meta:
    	prefix = ('api',)
     	components = (scaffold.Scaffolding,Drafts)

    class Scaffold:
        display_properties = ('created_by', 'created', 'Requested_By', 'Submission_Date','Buyer','Subject','Please_Select_Request_Type', 
            'Please_Select_Request_Area','Attachments')

    delete = scaffold.delete
    edit = scaffold.edit

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

	@route
	def datarequestform(self):
		self.context['user'] = users.get_current_user()

	@route
	def list(self):
		self.context['user'] = users.get_current_user()
		#self.context['user_email'] = self.session.get('user_email')
		
		if 'order_by_created_asc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_created_asc()
			self.context['c_order_by'] = 'desc'
		elif 'order_by_created_desc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_created_desc()
			self.context['c_order_by'] = 'asc'
		elif 'order_by_created_by_asc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_created_by_asc()
			self.context['cb_order_by'] = 'desc'
		elif 'order_by_created_by_desc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_created_by_desc()
			self.context['cb_order_by'] = 'asc'
		elif 'order_by_status_asc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_status_asc()
			self.context['status_order_by'] = 'desc'
		elif 'order_by_status_desc' in self.request.params:
			self.context['datarequests'] = Datarequest.order_by_status_desc()
			self.context['status_order_by'] = 'asc'
		else:
			self.context['datarequests'] = Datarequest.all()
			self.context['cb_order_by'] = 'asc'

	def add(self):
		return scaffold.add(self)

	def view(self,key):

		datarequest = self.util.decode_key(key).get()
		self.context['reqBy'] = datarequest.Requested_By
		self.context['subDate'] = datarequest.Submission_Date
		self.context['buyer'] = datarequest.Buyer
		self.context['subj'] = datarequest.Subject
		self.context['reqType'] = datarequest.Please_Select_Request_Type
		self.context['reqArea'] = datarequest.Please_Select_Request_Area
		self.context['comments'] = datarequest.Comments
		self.context['atch'] = datarequest.Attachments
		statusVar = datarequest.Status
		self.context['status'] = Utils.convertStatus(statusVar)

	@route
	def sendNotif(self):

		form = self.request.params

		action = form['action']
		reqBy = form['reqBy']
		subDate = form['subDate']
		buyer = form['buyer']
		subj = form['subj']
		reqType = form['reqType']
		reqArea = form['reqArea']
		comments = form['comments']
		atch = form['atch']
		status = form['status']
		additional_comments = form['addcomments']

		keyid = form['keyid']
		datarequest = self.util.decode_key(keyid).get()

		to = "merchandiseteam@testemail.com"
		
		if (comments == "" or comments == None):
			comments = "None"

		if (subj == "" or subj == None):
			subj = "None"

		if (additional_comments == "" or additional_comments == None):
			additional_comments = "None"

		# For Merchandise Team Approval
		if (action == "approve"):

			datarequest.Status = 3
			datarequest.put()
			status = "Approved"
			subject = "Woolies:Master Data Request Approval Notification"
			Datarequests.sendMail(status,reqBy,subDate,buyer,subj,reqType,reqArea,comments,atch,additional_comments,to,subject)

		# For Merchandise Team Rejection
		elif (action == "reject"):
			datarequest.Status = 4
			datarequest.put()
			status = "Rejected"
			subject = "Woolies:Master Data Request Rejection Notification"
			Datarequests.sendMail(status,reqBy,subDate,buyer,subj,reqType,reqArea,comments,atch,additional_comments,to,subject)

		return self.redirect(self.uri(handler='datarequests', action='list'))

	@classmethod
	def sendMail(self,status,reqBy,subDate,buyer,subj,reqType,reqArea,comments,atch,additional_comments,to,subject):

		msg_body = """\
		<html>
		<body>
		<span style="width: 600px; padding: 1px; background: #d3d3d3; display: block">

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
		                <p>Hi, <br/><br/><br/>The request for buyer's new line declaration is <span style="color: #ff502d"><strong>%s</strong></span> with the following details:</p>
		            </td>
		            <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
		        </tr>
		        <!-- opening -->

		        <!-- 1 liner 2 columns -->
		        <tr>
		            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
		            <td style="padding: 7px 0; padding-top: 15px; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requested By</span>
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
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Buyer</span>
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
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Subject</span>
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
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Request Type</span>
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
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Request Area</span>
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
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Attachments</span><br/>
		                <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
		            </td>
		            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
		        </tr>
		        <!-- 1 liner tall row important -->

		        <!-- 1 row 2 liner -->
		        <tr>
		            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
		            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">COMMENTS</span><br/>
		                <p style="color: #262626; font-size: 12px;">%s</p>
		            </td>
		            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
		        </tr>
		        <!-- 1 row 2 liner -->

		        <!-- 1 row 2 liner -->
		        <tr>
		            <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
		            <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
		                <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">COMMENTS FROM APPROVER</span><br/>
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
		</body>
		</html>
		""" % (status,reqBy,subDate,buyer,subj,reqType,reqArea,atch,comments,additional_comments)

		mail.send(to, subject, msg_body, str(users.get_current_user()))