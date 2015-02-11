from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from ..controllers.utils import Utils
from ..models.dc import Dc
from google.appengine.api import users
from ferris.core import mail
from ..models.stockreject import Stockreject
from ..controllers.users import Users
import logging
import urllib2

from ..models.vendor_list import VendorList
from plugins import directory
from app.component.drafts import Drafts

class Stockrejects(Controller):

    class Meta:
        prefix = ('api',)
        components = (scaffold.Scaffolding,Pagination,Upload,Drafts)
        pagination_limit = 10
        action_form = 'stockrejectform'

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
    def stockrejectform(self):
        form_key = self.context.get('form_key')
        def after_save(controller, container, item):
            form = item
            uiparams = self.request.params
            dateSent = uiparams['dateSent']
            user_email = controller.session.get('user_email')
            domainpath = controller.session.get('DOMAIN_PATH')

            # view_key = str(item.key.urlsafe())
            # encoded_param = urllib2.unquote('%3A') + view_key + "?key=" + form_key
            encoded_param = "?key=" + form_key

            self.sendNotif(form,user_email, domainpath,dateSent,encoded_param)

        self.events.scaffold_after_save += after_save
        dcs = Dc.get_dcs()
        self.context['dcs'] = dcs

        # User Info from global address
        try:
            userinfodict = directory.get_user_by_email(self.session.get('user_email'))
        except:
            userinfodict = None

        # Retrieves the Form Managers and save in the context
        form_mngr_key = self.context.get('first_group_approver').key.urlsafe()
        approverslist = Users.get_users_by_group(form_mngr_key)
        self.context['form_managers'] = approverslist

        vendors = VendorList.get_all()
        self.context['vendors'] = vendors

        if userinfodict:

            self.context['user_info_email'] = userinfodict.get('primaryEmail')
            self.context['user_info_fullname'] = userinfodict.get('name').get('fullName', '')
            #self.context['user_info_phone'] = userinfodict['phone']
            #self.context['fax'] = userinfodict['fax']

        self.context['PAGE_TITLE'] = 'Add new Stock Rejection Form'
        self.scaffold.redirect = '/stockrejects?key=' + form_key
        return scaffold.add(self)

    @route
    def list(self):

        self.context['user'] = self.session.get('user_email')
        self.context['user_isFormAdmin'] = self.context.get('user_isFormAdmin')

        frmkey = self.request.params['key']
        self.context['frmkey']  = frmkey

         #show all queries if manager of the form
        showAll = self.context.get('user_isManager')
        if self.request.get('order_by_created'):
            order = self.request.get('order_by_created') == 'desc'  and Stockreject.created_by or -Stockreject.created_by
        elif self.request.get('order_by_status')    :
            order = self.request.get('order_by_status') == 'desc'  and Stockreject.Status or -Stockreject.Status
        else:
            order = self.request.get('order_by_date') == 'desc'  and Stockreject.created or -Stockreject.created

        if showAll:
            self.context['stockrejects'] = Stockreject.query().order(order)
        else:
            self.context['stockrejects'] = Stockreject.query(Stockreject.created_by == users.get_current_user()).order(order)

        if not self.context['stockrejects'].fetch():

            return self.redirect(self.uri(action='stockrejectform', key=frmkey))

    @route
    def delete(self,key):
        selectedItem = self.util.decode_key(key).get()
        selectedItem.key.delete()
        frmkey = self.request.params['key']
        return self.redirect(self.uri(action='delete_suc', key=frmkey))

    @route
    def delete_suc(self):
        self.context['frmkey'] = self.request.params['key']
        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value

    def view(self,key):

        stockreject = self.util.decode_key(key).get()
        self.context['to'] = str(stockreject.To)
        self.context['cc'] = stockreject.CC
        self.context['subject'] = stockreject.Subject
        self.context['vendor'] = stockreject.Vendor
        self.context['returntype'] = stockreject.Return_Type
        self.context['carrier'] = stockreject.Carrier
        self.context['dateofarrival'] = stockreject.Date_of_Arrival
        self.context['timeofrejection'] = stockreject.Time_of_Rejection
        self.context['productother'] = stockreject.Product_Other

        self.context['purchaseorder'] = stockreject.Purchase_Order
        self.context['loadnumber'] = stockreject.Load_Number
        self.context['palletsreceived'] = stockreject.Pallets_Received
        self.context['palletsaffected'] = stockreject.Pallets_Affected
        self.context['cartonscffected'] = stockreject.Cartons_Affected
        self.context['replenishmentcontacted'] = stockreject.Replenishment_Contacted
        self.context['woolworthsprimaryfreight'] = stockreject.Woolworths_Primary_Freight
        self.context['comments'] = stockreject.Comments

        self.context['attachments'] = stockreject.Attachments

        self.context['download_link'] = Utils.generate_download_link(stockreject.Attachments)

        self.context['from'] = stockreject.From
        self.context['phone'] = stockreject.Phone
        self.context['fax'] = stockreject.Fax
        self.context['email'] = stockreject.Email
        self.context['dc'] = stockreject.DC

        self.context['keyid'] = stockreject.key.urlsafe()
        self.context['frmkey'] = self.request.params['frmkey']

        # this will serve all the session to context for template access
        for key, value in self.session.items():
            self.context[key] = value


    @classmethod
    def sendNotif(self,form,user_email, domain_path,dateSent,encoded_param):

        domain_path = str(domain_path)

        To  = form.To
        CC = form.CC
        Subject  = form.Subject
        Vendor = form.Vendor
        Return_Type = form.Return_Type
        Carrier = form.Carrier
        Date_of_Arrival = form.Date_of_Arrival
        Time_of_Rejection = form.Time_of_Rejection
        Product_Other = form.Product_Other
        Purchase_Order  = form.Purchase_Order
        Load_Number  = form.Load_Number
        Pallets_Received  = form.Pallets_Received
        Pallets_Affected  = form.Pallets_Affected
        Cartons_Affected  = form.Cartons_Affected
        Replenishment_Contacted  = form.Replenishment_Contacted
        Woolworths_Primary_Freight  = form.Woolworths_Primary_Freight
        Comments  = form.Comments
        Attachments  = form.Attachments
        From = form.From
        Phone = form.Phone
        Fax = form.Fax
        Email= form.Email
        DC= form.DC

        Stockrejects.sendMail(dateSent,To,CC,user_email,Subject,Vendor,Return_Type,Carrier,Date_of_Arrival,Time_of_Rejection,Product_Other,Purchase_Order,Load_Number,Pallets_Received,Pallets_Affected,Cartons_Affected,Replenishment_Contacted,Woolworths_Primary_Freight,Comments,Attachments,From,Phone,Fax,Email,DC, domain_path,encoded_param)

    @classmethod
    def sendMail(self,dateSent,To,CC,user_email,Subject,Vendor,Return_Type,Carrier,Date_of_Arrival,Time_of_Rejection,Product_Other,Purchase_Order,Load_Number,Pallets_Received,Pallets_Affected,Cartons_Affected,Replenishment_Contacted,Woolworths_Primary_Freight,Comments,Attachments,From,Phone,Fax,Email,DC, domain_path,encoded_param):

        attchmnt = Utils.generate_download_link(Attachments)

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
                        <td style="padding: 0; margin: 0; width: 50px; height: 80px; background: #2c3742;">&nbsp;</td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 80px; background: #2c3742; color: #fff; text-align: justify;">
                            <p>Hi everyone, <br/><br/>A Stock has been rejected with the following details: </p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px; height: 80px; background: #2c3742;">&nbsp;</td>
                    </tr>
                    <!-- opening -->

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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Vendor</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Return Type</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Carrier</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Date of Arrival</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Time of Rejection</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Product Other</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Purchase Order</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Load Number</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Cartons Affected</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Replenishment Contacted</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Woolworths Primary Freight</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Comments</span><br/>
                            <p style="color: #262626; font-size: 12px;">%s</p>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 row 2 liner -->

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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Phone</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Fax</span>
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
                            <span style="font-size: 11px; color: #7d7d7d; font-weight: bold; text-transform: uppercase;">Email</span><br/>
                            <span style="margin-top: 10px; color: #3b9ff3;">%s</span>
                        </td>
                        <td style="padding: 0; margin: 0; width: 50px;">&nbsp;</td>
                    </tr>
                    <!-- 1 liner tall row important -->

                    <!-- Footer -->
                     <tr>
                        <td style="padding: 0; margin: 0; width: 50px; height: 50px;"></td>
                        <td colspan="2" style="padding: 0; margin: 0; width: 500px; height: 100px;">
                            <p style="color: #909090; font-size: 12px; text-align: left;">Click here to view list<br/>
                                <a style='color: #3b9ff3;' target='_blank' href='http://%s/stockrejects%s'>http://%s/stockrejects%s</a>
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
        """ % (user_email, DC, Vendor,Return_Type ,Carrier ,Date_of_Arrival ,Time_of_Rejection ,
            Product_Other ,Purchase_Order ,Load_Number ,Pallets_Received, Pallets_Affected ,Cartons_Affected,
            Replenishment_Contacted, Woolworths_Primary_Freight, Comments, attchmnt, From,Phone,Fax, Email,
            domain_path, encoded_param, domain_path, encoded_param)

        mail.send(To, Subject, msg_body, str(user_email),cc=CC)
