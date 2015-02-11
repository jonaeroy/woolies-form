from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from ..models.vendor_list import VendorList


class VendorLists(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination)
        pagination_limit = 10

    class Scaffold:
        display_properties = ('vendor',)

    add = scaffold.add
    edit = scaffold.edit
    view = scaffold.view
    delete = scaffold.delete

    def list(self):

        for key, value in self.session.items():
            self.context[key] = value

        self.context['data'] = VendorList.get_all()

    @route
    def save_import(self):
        vendor = self.request.get('VENDOR NAME')
        vendorList = VendorList(vendor = vendor)
        vendorList.put()

        result = True
        return self.util.stringify_json(result);