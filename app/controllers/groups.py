from ferris import Controller, scaffold
from ..models.group import Group

class Groups(Controller):
    class Meta:
        prefixes = ('api',)
        components = (scaffold.Scaffolding,)

    class Scaffold:
        display_properties = ('name', '')

    edit = scaffold.edit
    #list = scaffold.list

    def list(self):        

        for key, value in self.session.items():
            self.context[key] = value
        self.context['data']= Group.all()
        self.context['PAGE_TITLE'] = 'Manage Groups'

    add = scaffold.add
    view = scaffold.view
    add = scaffold.add
    delete = scaffold.delete