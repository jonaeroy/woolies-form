from ferris import Controller, scaffold, route
from ferris.components.pagination import Pagination
from ..models.dc import Dc


class Dcs(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination)
        pagination_limit = 10

    class Scaffold:
        display_properties = ('location_number', 'location_name')

    def add(self):
        return scaffold.add(self)

    #list = scaffold.list
    def list(self):

        for key, value in self.session.items():
            self.context[key] = value
        self.context['data'] = Dc.get_dcs()

    def edit(self, key):
        return scaffold.edit(self, key)

    def view(self, key):
        return scaffold.view(self, key)

    def delete(self, key):
        return scaffold.delete(self, key)

    @route
    def dc_import(self):
        return

    @route
    def save_import(self):
        number = self.request.get('Loc no')
        name = self.request.get('Loc Name')
        dc = Dc(location_number = number,
                    location_name=name)
        dc.put()

        result = True
        return self.util.stringify_json(result);