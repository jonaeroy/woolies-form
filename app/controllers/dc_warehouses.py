from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from ..models.dc_warehouse import DcWarehouse


class DcWarehouses(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination)
        pagination_limit = 10

    class Scaffold:
        display_properties = ('dc_name', 'address', 'maintenance_or_dc_manager', 'email', 'strategy')

    #add = scaffold.add
    edit = scaffold.edit
    view = scaffold.view
    delete = scaffold.delete

    def list(self):

        for key, value in self.session.items():
            self.context[key] = value

        self.context['data'] = DcWarehouse.get_all()

    def add(self):
        return scaffold.add(self)

    @route
    def dc_import(self):
        return

    @route
    def save_import(self):
        name = self.request.get('DC Name')
        address = self.request.get('Address')
        maint = self.request.get('Maint/DC Mgr')
        mobile = self.request.get('Mobile Number')
        email = self.request.get('E-mail')
        strategy = self.request.get('Strategy')

        dcwarehouse = DcWarehouse(dc_name = name,
                    address= address,
                    maintenance_or_dc_manager=maint,
                    mobile_number=mobile,
                    email_address=email,
                    strategy=strategy)
        dcwarehouse.put()

        result = True
        return self.util.stringify_json(result);
