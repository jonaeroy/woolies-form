from ferris import Controller, scaffold, route
from ..models.store import Store
from ..models.costcentre import Costcentre
from ferris.components.pagination import Pagination
from google.appengine.api import users
from ferris.core import mail
from ..controllers.users import Users
from ..models.courierbook import Courierbook
import logging
import urllib2
from plugins import directory
from app.component.drafts import Drafts

class Courierbooks(Controller):

    class Meta:
        prefix = ('admin',)
        components = (scaffold.Scaffolding,Pagination,Drafts)
        pagination_limit = 10
        action_form = 'courierbookingform'

    @route
    def draft_action(self):
        self.components.drafts.save(self.request.params)
        return 200

    @route
    def clear_draft_action(self):
        self.components.drafts.clear()
        return 200

    @route
    def courierbookingform(self):
        self.context['stores'] = self.util.stringify_json(Store.all_stores())
        self.context['user_fullname'] = self.session.get('user_fullname')
        self.context['costcentres'] = Costcentre.all_costcentres()

        try:
            userinfodict = directory.get_user_by_email(self.session.get('user_email'))
        except:
            userinfodict = None

        if userinfodict:
            self.context['user_fullname'] = userinfodict.get('name').get('fullName')


    @route
    def add(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = self.request.params
            user_email = self.session.get('user_email')
            domainpath = self.session.get('DOMAIN_PATH')
            tmp = self.context.get('first_group_approver').key.urlsafe()
            to = Users.get_user_list_by_group(tmp)

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            Courierbooks.sendNotif(form,to,user_email, domainpath, encoded_param)

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
        item_data = self.util.decode_key(key).get()

        item_data.Full_Name = form['Full_Name']
        item_data.Contact_Number = form['Contact_Number']

        item_data.Store_No_Pick_Up = form['Store_No_Pick_Up']
        item_data.Store_Name_Pick_Up = form['Store_Name_Pick_Up']
        item_data.Address1_Pick_Up = form['Address1_Pick_Up']
        item_data.Address2_Pick_Up = form['Address2_Pick_Up']
        item_data.Suburb_Pick_Up = form['Suburb_Pick_Up']
        item_data.State_Pick_Up = form['State_Pick_Up']
        item_data.Post_Code_Pick_Up = form['Post_Code_Pick_Up']

        item_data.Store_No_Dest = form['Store_No_Dest']
        item_data.Store_Name_Dest = form['Store_Name_Dest']
        item_data.Address1_Dest = form['Address1_Dest']
        item_data.Address2_Dest = form['Address2_Dest']
        item_data.Suburb_Dest = form['Suburb_Dest']
        item_data.State_Dest = form['State_Dest']
        item_data.Post_Code_Dest = form['Post_Code_Dest']

        item_data.Reason_For_Courier = form['Reason_For_Courier']
        item_data.Cost_Centre = form['Cost_Centre']
        item_data.Description_of_Package = form['Description_of_Package']
        item_data.Length = form['Length']
        item_data.Width = form['Width']
        item_data.Height = form['Height']
        item_data.Weight = form['Weight']
        item_data.Quantity = form['Quantity']
        item_data.Insurance_required = form['Insurance_required']
        item_data.Ready_to_be_collected = form['Ready_to_be_collected']
        item_data.From = form['From']
        item_data.Please_select_the_Courier_Vehicle_size_required = form['Please_select_the_Courier_Vehicle_size_required']

        item_data.put()

        return self.redirect(self.uri(action='view', key=key, frmkey=frmkey))

    @route
    def update(self, key):

        item = self.util.decode_key(key).get()
        self.context['item'] = item
        self.context['stores'] = self.util.stringify_json(Store.all_stores())
        self.context['user_fullname'] = self.session.get('user_fullname')
        self.context['costcentres'] = Costcentre.all_costcentres()
        self.context['frmkey']  = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        #self.context['isManager'] = self.context.get('user_isManager')
        self.context['user_isFormAdmin'] = self.context.get('user_isFormAdmin')

        frmkey = self.request.params['key']
        self.context['frmkey']  = frmkey

        #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        logging.info('show All ==========> ' + str(showAll))
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Courierbook.created_by or -Courierbook.created_by
        elif self.request.get('order_by_status')    :
            order = self.request.get('order_by_status') == 'desc'  and Courierbook.Status or -Courierbook.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Courierbook.created or -Courierbook.created

        if showAll:
            self.context['courierbooks'] = Courierbook.query().order(order)
        else:
            self.context['courierbooks'] = Courierbook.query(Courierbook.created_by == users.get_current_user()).order(order)

        if not self.context['courierbooks'].fetch():

            return self.redirect(self.uri(action='courierbookingform', key=frmkey))

    def view(self,key):

        courierbook = self.util.decode_key(key).get()
        self.context['key'] = courierbook.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']
        self.context['costcentres'] = Costcentre.all_costcentres()
        self.context['courierbook'] = courierbook

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    @classmethod
    def sendNotif(self,form,to,user_email, domain_path, encoded_param):

        domain_path = str(domain_path)
        dateSent  = form['dateSent']
        Subject = "Dan Murphy's Booking Request Notifications"

        # To  = form['To']
        To  = to
        Full_Name  = form['Full_Name']
        Contact_Number = form['Contact_Number']
        #Pick Up Store
        Store_No_Pick_Up = form['Store_No_Pick_Up']
        Store_Name_Pick_Up = form['Store_Name_Pick_Up']
        Address1_Pick_Up = form['Address1_Pick_Up']
        Address2_Pick_Up  = form['Address2_Pick_Up']
        Suburb_Pick_Up  = form['Suburb_Pick_Up']
        State_Pick_Up  = form['State_Pick_Up']
        Post_Code_Pick_Up  = form['Post_Code_Pick_Up']
        #Destination Store
        Store_No_Dest = form['Store_No_Dest']
        Store_Name_Dest = form['Store_Name_Dest']
        Address1_Dest = form['Address1_Dest']
        Address2_Dest  = form['Address2_Dest']
        Suburb_Dest  = form['Suburb_Dest']
        State_Dest  = form['State_Dest']
        Post_Code_Dest  = form['Post_Code_Dest']

        Reason_For_Courier  = form['Reason_For_Courier']
        Cost_Centre  = form['Cost_Centre']

        #Package Details
        Description_of_Package = form['Reason_For_Courier']
        Length = form['Length']
        Width = form['Width']
        Height = form['Height']
        Weight = form['Weight']
        Quantity = form['Quantity']
        Insurance_required = form['Insurance_required']
        Ready_to_be_collected = form['Ready_to_be_collected']
        From = form['From']
        Please_select_the_Courier_Vehicle_size_required = form['Please_select_the_Courier_Vehicle_size_required']

        Courierbooks.sendMail(To,dateSent,user_email,Subject,Full_Name,Contact_Number,
            Store_No_Pick_Up,Store_Name_Pick_Up,Address1_Pick_Up,Address2_Pick_Up,
            Suburb_Pick_Up,State_Pick_Up,Post_Code_Pick_Up,
            Store_No_Dest,Store_Name_Dest,Address1_Dest,Address2_Dest,
            Suburb_Dest,State_Dest,Post_Code_Dest,Reason_For_Courier,Cost_Centre,
            Description_of_Package,Length,Width,Height,Weight,Quantity,Insurance_required,
            Ready_to_be_collected,From,
            Please_select_the_Courier_Vehicle_size_required,domain_path,encoded_param)

    @classmethod
    def sendMail(self,To,dateSent,user_email,Subject,Full_Name,Contact_Number,
            Store_No_Pick_Up,Store_Name_Pick_Up,Address1_Pick_Up,Address2_Pick_Up,
            Suburb_Pick_Up,State_Pick_Up,Post_Code_Pick_Up,
            Store_No_Dest,Store_Name_Dest,Address1_Dest,Address2_Dest,
            Suburb_Dest,State_Dest,Post_Code_Dest,Reason_For_Courier,Cost_Centre,
            Description_of_Package,Length,Width,Height,Weight,Quantity,Insurance_required,
            Ready_to_be_collected,From,
            Please_select_the_Courier_Vehicle_size_required,domain_path,encoded_param):

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
                        <p>Hi, <br/><br/><br/>A request has been booked with the following details:</p>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px; height: 150px; background: #2c3742;">&nbsp;</td>
                </tr>
                <!-- opening -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Requestor</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Contact Number</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">PICK UP STORE</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store No.</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Name</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Address 1</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Address 2</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Suburb</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Postcode</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">DESTINATION STORE</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store No.</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Store Name</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Address 1</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Address 2</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

                <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Suburb</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Postcode</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Reason for Courier</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

               <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Cost Centre</span>
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
                        <span style="font-size: 12px; color: #b85e80; font-weight: bold; text-transform: uppercase;">PACKAGE DETAILS</span>
                    </td>
                    <td style="padding: 7px 0; margin: 0; width: 80px; border-bottom: 1px solid #d8dee3;">

                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner 2 columns -->

                <!-- 1 liner tall row important -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td colspan="2" style="padding: 20px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Description of Package</span><br/>
                        <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                    </td>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                </tr>
                <!-- 1 liner tall row important -->

               <!-- 1 liner 2 columns -->
                <tr>
                    <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    <td style="padding: 7px 0; margin: 0; width: 420px; border-bottom: 1px solid #d8dee3;">
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Length</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Width</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Height</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Weight</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Quantity</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Insurance required</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Ready to be collected</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">From</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Courier Vehicle size</span>
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
                        <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Submitted By</span>
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
                            <a style='color: #3b9ff3;' target='_blank' href='http://%s/courierbooks%s'>http://%s/courierbooks%s</a>
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
        """ % (Full_Name,Contact_Number,
            Store_No_Pick_Up,Store_Name_Pick_Up,Address1_Pick_Up,Address2_Pick_Up,
            Suburb_Pick_Up,State_Pick_Up,Post_Code_Pick_Up,
            Store_No_Dest,Store_Name_Dest,Address1_Dest,Address2_Dest,
            Suburb_Dest,State_Dest,Post_Code_Dest,Reason_For_Courier,Cost_Centre,
            Description_of_Package,Length, Width, Height, Weight, Quantity,
            Insurance_required, Ready_to_be_collected, From,
            Please_select_the_Courier_Vehicle_size_required,user_email,
            domain_path, encoded_param,  domain_path, encoded_param)

        mail.send(To, Subject, msg_body, str(user_email))
