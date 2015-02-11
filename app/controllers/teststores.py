from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from google.appengine.api import users
from ferris.core import mail
import logging
from ..models.teststore import Teststore
from ..controllers.users import Users
import urllib2
from ..controllers.utils import Utils
import datetime
from app.component.drafts import Drafts
from app.component.split_view import SplitView

class Teststores(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding, Pagination, Drafts)
        pagination_limit = 10
        action_form = 'teststorereqform'

    class Scaffold:
        display_properties = ('created_by', 'created', 'Project_Name', 
            'Requested_By','Project_No_ER1','Banner1','Start_Date1','End_Date1','Store_Allocated1')

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
    def teststoreallocate(self,key):
        teststore = self.util.decode_key(key).get()
        self.context['teststore'] = teststore

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def teststorereqform(self):
        self.context['user'] = self.session.get('user_email')

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def delete(self,key):
        teststore = self.util.decode_key(key).get()
        teststore.key.delete()
        frmkey = self.request.params['key']
        return self.redirect(self.uri(action='delete_suc', key=frmkey))

    @route
    def delete_suc(self):

        self.context['frmkey'] = self.request.params['key']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        frmkey = self.request.params['key']
        self.context['frmkey'] = frmkey

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc' and Teststore.created_by or -Teststore.created_by
        elif self.request.get('order_by_status'):
            order = self.request.get('order_by_status') == 'desc' and Teststore.Store_Allocated1 or -Teststore.Store_Allocated1
        else:
            order = self.request.get('order_by_date') == 'desc' and Teststore.created or -Teststore.created

        if showAll:
            self.context['is_Normal_User'] = False
            self.context['teststores'] = Teststore.query().order(order)
        else:
            self.context['is_Normal_User'] = True
            self.context['teststores'] = Teststore.query(Teststore.created_by == users.get_current_user()).order(order)

        if not self.context['teststores'].fetch():

            return self.redirect(self.uri(action='teststorereqform', key=frmkey))


    @route
    def add(self):

        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = self.request.params
            # Check if the field is empty and save
            subbanner1 = Teststores.checkEmptyField(self.request.get('Sub_Banner1'))
            subbanner2 = Teststores.checkEmptyField(self.request.get('Sub_Banner2'))
            subbanner3 = Teststores.checkEmptyField(self.request.get('Sub_Banner3'))
            subbanner4 = Teststores.checkEmptyField(self.request.get('Sub_Banner4'))
            sco1 = Teststores.checkEmptyField(self.request.get('SCO1'))
            sco2 = Teststores.checkEmptyField(self.request.get('SCO2'))
            sco3 = Teststores.checkEmptyField(self.request.get('SCO3'))
            sco4 = Teststores.checkEmptyField(self.request.get('SCO4'))

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            user_email = self.session.get('user_email')
            domainpath = self.session.get('DOMAIN_PATH')
            tmp = self.context.get('first_group_approver').key.urlsafe()
            to = Users.get_user_list_by_group(tmp)
            action = 'new'
            Teststores.sendNotifFromUser(form, to, user_email, domainpath, subbanner1, subbanner2, subbanner3, subbanner4, sco1, sco2, sco3, sco4,encoded_param,action)

        self.events.scaffold_after_save += after_save

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
        to = form['fg_approver']

        logging.info('FG APPROVER ======================>' + str(to))
        item_data = self.util.decode_key(key).get()

        item_data.Project_Name = form['Project_Name']
        item_data.Requested_By = form['Requested_By']
        item_data.Project_No_ER = form['Project_No_ER']

        item_data.Banner1 = form['Banner1']
        try:
            item_data.Sub_Banner1 = form['Sub_Banner1']
        except:
            item_data.Sub_Banner1 = ""
        try:
            item_data.SCO1 = form['SCO1']
        except:
            item_data.SCO1 = ""
        item_data.Environment1 = form['Environment1']
        item_data.Start_Date1 = form['Start_Date1']
        item_data.End_Date1 = form['End_Date1']
        item_data.Software_Version_Level1 = form['Software_Version_Level1']
        item_data.Store_Allocated1 = form['Store_Allocated1']

        item_data.Banner2 = form['Banner2']
        try:
            item_data.Sub_Banner2 = form['Sub_Banner2']
        except:
            item_data.Sub_Banner2 = ""
        try:
            item_data.SCO2 = form['SCO2']
        except:
            item_data.SCO2 = ""
        item_data.Environment2 = form['Environment2']
        item_data.Start_Date2 = form['Start_Date2']
        item_data.End_Date2 = form['End_Date2']
        item_data.Software_Version_Level2 = form['Software_Version_Level2']
        item_data.Store_Allocated2 = form['Store_Allocated2']

        item_data.Banner3 = form['Banner3']
        try:
            item_data.Sub_Banner3 = form['Sub_Banner3']
        except:
            item_data.Sub_Banner3 = ""
        try:
            item_data.SCO3 = form['SCO3']
        except:
            item_data.SCO3 = ""
        item_data.Environment3 = form['Environment3']
        item_data.Start_Date3 = form['Start_Date3']
        item_data.End_Date3 = form['End_Date3']
        item_data.Software_Version_Level3 = form['Software_Version_Level3']
        item_data.Store_Allocated3 = form['Store_Allocated3']

        item_data.Banner4 = form['Banner4']
        try:
            item_data.Sub_Banner4 = form['Sub_Banner4']
        except:
            item_data.Sub_Banner4 = ""
        try:
            item_data.SCO4 = form['SCO4']
        except:
            item_data.SCO4 = ""
        item_data.Environment4 = form['Environment4']
        item_data.Start_Date4 = form['Start_Date4']
        item_data.End_Date4 = form['End_Date4']
        item_data.Software_Version_Level4 = form['Software_Version_Level4']
        item_data.Store_Allocated4 = form['Store_Allocated4']

        item_data.Test_Purpose_Applications_Required = form['Test_Purpose_Applications_Required']
        
        item_data.put()

        form = self.request.params
        # Check if the field is empty and save
        subbanner1 = self.checkEmptyField(self.request.get('Sub_Banner1'))
        subbanner2 = self.checkEmptyField(self.request.get('Sub_Banner2'))
        subbanner3 = self.checkEmptyField(self.request.get('Sub_Banner3'))
        subbanner4 = self.checkEmptyField(self.request.get('Sub_Banner4'))
        sco1 = self.checkEmptyField(self.request.get('SCO1'))
        sco2 = self.checkEmptyField(self.request.get('SCO2'))
        sco3 = self.checkEmptyField(self.request.get('SCO3'))
        sco4 = self.checkEmptyField(self.request.get('SCO4'))

        # view_key = str(item.key.urlsafe())
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + frmkey

        user_email = self.session.get('user_email')
        domainpath = self.session.get('DOMAIN_PATH')

        action = 'edit'

        self.sendNotifFromUser(form, to, user_email, domainpath, subbanner1, subbanner2, subbanner3, subbanner4, sco1, sco2, sco3, sco4,encoded_param, action)

        return self.redirect(self.uri(action='list', key=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['frmkey']  = self.request.params['frmkey']

        tmp = self.context.get('first_group_approver').key.urlsafe()
        to = Users.get_user_list_by_group(tmp)
        self.context['fg_approver'] = to

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self,key):

        teststore = self.util.decode_key(key).get()
        current_user = self.session.get('user_email')
        self.context['teststore'] = teststore
        self.context['frmkey'] = self.request.params['frmkey']
        pending = "Pending for QA Team Allocation"

        if(teststore.Store_Allocated1 == ""):
            teststore.Store_Allocated1 = pending
            self.context['storeallocated1'] = teststore.Store_Allocated1
        else:
            self.context['storeallocated1'] = teststore.Store_Allocated1
        
        if(teststore.Store_Allocated2 == ""):
            teststore.Store_Allocated2 = pending
            self.context['storeallocated2'] = teststore.Store_Allocated2
        else:
            self.context['storeallocated2'] = teststore.Store_Allocated2

        if(teststore.Store_Allocated3 == ""):
            teststore.Store_Allocated3 = pending
            self.context['storeallocated3'] = teststore.Store_Allocated3
        else:
            self.context['storeallocated3'] = teststore.Store_Allocated3

        if(teststore.Store_Allocated4 == ""):
            teststore.Store_Allocated4 = pending
            self.context['storeallocated4'] = teststore.Store_Allocated4
        else:
            self.context['storeallocated4'] = teststore.Store_Allocated4

        if str(current_user) == str(teststore.created_by):
            self.context['is_requestor'] = True
        else:
            self.context['is_requestor'] = False

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def checkEmptyField(self,field):

        if(field=="" or field is None):
            field = "None"
            return field
        else:
            return field

    @classmethod
    def sendNotifFromUser(self,form,to,user_email,domainpath,subbanner1,subbanner2,subbanner3,subbanner4,sco1,sco2,sco3,sco4,encoded_param, action):

        projectname = form['Project_Name']
        requestedby = form['Requested_By']
        projectnoer = form['Project_No_ER']
        testpurposeapplicationsrequired = form['Test_Purpose_Applications_Required']
        createdby = form['createdby']
        dateSent  = form['dateSent']

        #Banner 1
        banner1 = form['Banner1']
        environment1 = form['Environment1']
        startdate1 = form['Start_Date1']
        enddate1 = form['End_Date1']
        softwareversionlevel1 = form['Software_Version_Level1']
        storeallocated1 = form['Store_Allocated1']

        #Banner 2
        banner2 = form['Banner2']
        environment2 = form['Environment2']
        startdate2 = form['Start_Date2']
        enddate2 = form['End_Date2']
        softwareversionlevel2 = form['Software_Version_Level2']
        storeallocated2 = form['Store_Allocated2']

        #Banner 3
        banner3 = form['Banner3']
        environment3 = form['Environment3']
        startdate3 = form['Start_Date3']
        enddate3 = form['End_Date3']
        softwareversionlevel3 = form['Software_Version_Level3']
        storeallocated3 = form['Store_Allocated3']

        #Banner 4
        banner4 = form['Banner4']
        environment4 = form['Environment4']
        startdate4 = form['Start_Date4']
        enddate4 = form['End_Date4']
        softwareversionlevel4 = form['Software_Version_Level4']
        storeallocated4 = form['Store_Allocated4']

        if action == 'edit':
            status = 'Edited'
            subject = "Change in QA Store Request: Test Store Request Form"
        else:
            status = 'Sent'
            subject = "QA Store Request: Test Store Request Form"

        Teststores.sendMailFromUser(projectname, createdby, dateSent, requestedby, projectnoer, 
            banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
            banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2, 
            banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3, 
            banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4, 
            testpurposeapplicationsrequired, 
            to, subject,user_email,domainpath,encoded_param,status)

    @classmethod
    def sendMailFromUser(self,
        projectname,createdby,dateSent,
        requestedby,
        projectnoer,
        banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
        banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2,
        banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3,
        banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4,
        testpurposeapplicationsrequired,
        to,
        subject,
        user_email,
        domainpath,encoded_param,status):

        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

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
                        <p>Hi, <br/><br/><br/>The request for QA Test Store has been <span style="color: #ff502d">%s</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 15px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Request Creator</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span> on <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Project Name</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Project Number / ER</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <tr>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                </tr>


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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <tr>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                </tr>

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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <tr>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                </tr>

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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <tr>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                </tr>

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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <tr>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                    <td style="height: 20px;"></td>
                </tr>

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Test Purpose/Applications Required</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-weight: bold; color: #009900;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- Footer -->
                 <tr>
                    <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                    <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                        <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/teststores%s'>http://%s/teststores%s</a>
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
        """ % (status, date_time, current_user ,createdby,dateSent,projectname,requestedby,projectnoer,
            banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
            banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2, 
            banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3, 
            banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4, 
            testpurposeapplicationsrequired,domainpath,encoded_param,domainpath,encoded_param)

        mail.send(to, subject, msg_body, str(user_email))

    @route
    def sendNotif(self):

        form = self.request.params
        domainpath = self.session.get('DOMAIN_PATH')
        user_email = self.session.get('user_email')
        dateSent  = form['dateSent']

        projectname = form['Project_Name']
        requestedby = form['Requested_By']
        projectnoer = form['Project_No_ER']
        testpurposeapplicationsrequired = form['Test_Purpose_Applications_Required']

        #Banner 1
        banner1 = form['Banner1']
        subbanner1 = form['Sub_Banner1']
        sco1 = form['SCO1']
        environment1 = form['Environment1']
        startdate1 = form['Start_Date1']
        enddate1 = form['End_Date1']
        softwareversionlevel1 = form['Software_Version_Level1']
        storeallocated1 = form['Store_Allocated1']

        #Banner 2
        banner2 = form['Banner2']
        subbanner2 = form['Sub_Banner2']
        sco2 = form['SCO2']
        environment2 = form['Environment2']
        startdate2 = form['Start_Date2']
        enddate2 = form['End_Date2']
        softwareversionlevel2 = form['Software_Version_Level2']
        storeallocated2 = form['Store_Allocated2']

        #Banner 3
        banner3 = form['Banner3']
        subbanner3 = form['Sub_Banner3']
        sco3 = form['SCO3']
        environment3 = form['Environment3']
        startdate3 = form['Start_Date3']
        enddate3 = form['End_Date3']
        softwareversionlevel3 = form['Software_Version_Level3']
        storeallocated3 = form['Store_Allocated3']

        #Banner 4
        banner4 = form['Banner4']
        subbanner4 = form['Sub_Banner4']
        sco4 = form['SCO4']
        environment4 = form['Environment4']
        startdate4 = form['Start_Date4']
        enddate4 = form['End_Date4']
        softwareversionlevel4 = form['Software_Version_Level4']
        storeallocated4 = form['Store_Allocated4']

        reqbyemail = form['reqbyemail']
        keyid = form['keyid']
        teststore = self.util.decode_key(keyid).get()

        form_key = self.context.get('form_key')
        # view_key = str(keyid)
        # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
        encoded_param = "?key=" + form_key

        to = reqbyemail
        
        if (testpurposeapplicationsrequired == "" or testpurposeapplicationsrequired is None):
            testpurposeapplicationsrequired = "None"

        #Updates the User Request based on the store allocated by QA team
        teststore.Store_Allocated1 = storeallocated1
        teststore.Store_Allocated2 = storeallocated2
        teststore.Store_Allocated3 = storeallocated3
        teststore.Store_Allocated4 = storeallocated4
        teststore.put()

        subject = "QA Store Request: Store Allocation Completed"

        Teststores.sendMail(dateSent,projectname,requestedby,projectnoer,
            banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
            banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2, 
            banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3, 
            banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4,
            testpurposeapplicationsrequired,to,subject,domainpath,user_email,encoded_param)

        return self.redirect(self.uri(action='list', key=form_key))

    @classmethod
    def sendMail(self,dateSent,projectname,requestedby,projectnoer,
        banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
        banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2, 
        banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3, 
        banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4,
        testpurposeapplicationsrequired,to,subject,domainpath,user_email,encoded_param):

        current_user = str(users.get_current_user())
        date_time = Utils.localize_datetime(datetime.datetime.now())

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
                            <p>Hi, <br/><br/><br/>The request for QA Test Stores has been <span style="color: #ff502d">Allocated</span> on <span style="color: #ff502d">%s</span> 
                        by %s with the following details:</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated By</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Project Name</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Project Number / ER</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                        </td>
                        <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-weight: bold; color: #009900;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner 2 columns -->

                    <tr>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                    </tr>

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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                        </td>
                        <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-weight: bold; color: #009900;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner 2 columns -->

                    <tr>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                    </tr>

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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                        </td>
                        <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-weight: bold; color: #009900;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner 2 columns -->

                    <tr>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                    </tr>

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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Sub-Banner</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">SCO</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Environment</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Start Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">End Date</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Software Version Level</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Allocated</span>
                        </td>
                        <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-weight: bold; color: #009900;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner 2 columns -->

                    <tr>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                        <td style="height: 20px;"></td>
                    </tr>

                    <!-- 1 liner 2 columns -->
                    <tr>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                        <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Test Purpose/Applications Required</span>
                        </td>
                        <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">
                            <span style="font-weight: bold; color: #009900;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner 2 columns -->

                    <!-- Footer -->
                     <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                            <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/teststores%s'>http://%s/teststores%s</a>
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
        """ % (date_time, current_user ,user_email, projectname,requestedby,projectnoer,
            banner1, subbanner1, sco1, environment1, startdate1, enddate1, softwareversionlevel1, storeallocated1,
            banner2, subbanner2, sco2, environment2, startdate2, enddate2, softwareversionlevel2, storeallocated2, 
            banner3, subbanner3, sco3, environment3, startdate3, enddate3, softwareversionlevel3, storeallocated3, 
            banner4, subbanner4, sco4, environment4, startdate4, enddate4, softwareversionlevel4, storeallocated4,
            testpurposeapplicationsrequired, domainpath, encoded_param, domainpath, encoded_param)

        mail.send(to, subject, msg_body, str(user_email))


