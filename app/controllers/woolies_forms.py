from ferris import Controller, scaffold, route_with
from ..models.woolies_form import WooliesForm
from google.appengine.ext import ndb

class WooliesForms(Controller):
    class Meta:
        prefixes = ('api',)
        components = (scaffold.Scaffolding,)

    class Scaffold:
        display_properties = ('name', 'first_level_manager', 'second_level_manager')

    edit = scaffold.edit

    def list(self):

        for key, value in self.session.items():
            self.context[key] = value
        self.context['data'] = WooliesForm.all()
        self.context['PAGE_TITLE'] = 'Manage Forms'

    def add(self):  
        for key, value in self.session.items():
            self.context[key] = value

        self.context['form'] = WooliesForm.all()
        scaffold.add

    @route_with(template='/form/save/<group_one_key>/<group_two_key>/<form_key>')
    def save_manager_of_form(self, group_one_key, group_two_key, form_key):
        error = False
        form_key = ndb.Key(urlsafe=form_key)

        if group_one_key:
            group_one_key = ndb.Key(urlsafe=group_one_key)
        else:
            error = True

        if not group_two_key == 'None':
            group_two_key = ndb.Key(urlsafe=group_two_key)

        else:
            group_two_key = ndb.Key('Group', 'None')

        if not error:
            form = form_key.get()
            form.first_level_manager = group_one_key
            form.second_level_manager = group_two_key
            form.put()

        if not error:
            result = {'success': 'true'}
        else:
            result = {'success': 'false'}

        return self.util.stringify_json(result)


    @route_with(template='/form/approver/1/save/<group_key>/<form_key>')
    def save_form_approver_one(self, group_key, form_key):
        error = False
        form_key = ndb.Key(urlsafe=form_key)

        if group_key:
            if group_key == 'None':
                group_key = ndb.Key('Group', 'None')
            else:
                group_key = ndb.Key(urlsafe=group_key)
        else:
            error = True

        if not error:
            form = form_key.get()
            form.first_level_manager = group_key
            form.put()

        if not error:
            result = {'success': 'true'}
        else:
            result = {'success': 'false'}

        return self.util.stringify_json(result)


    @route_with(template='/form/approver/2/save/<group_key>/<form_key>')
    def save_form_approver_two(self, group_key, form_key):
        error = False
        form_key = ndb.Key(urlsafe=form_key)

        if group_key:
            if group_key == 'None':
                group_key = ndb.Key('Group', 'None')
            else:
                group_key = ndb.Key(urlsafe=group_key)
        else:
            error = True

        if not error:
            form = form_key.get()
            form.second_level_manager = group_key
            form.put()

        if not error:
            result = {'success': 'true'}
        else:
            result = {'success': 'false'}

        return self.util.stringify_json(result)

    @route_with(template='/form/admin/save/<group_key>/<form_key>')
    def save_form_admin(self, group_key, form_key):
        error = False
        form_key = ndb.Key(urlsafe=form_key)

        if group_key:
            group_key = ndb.Key(urlsafe=group_key)
        else:
            error = True

        if not error:
            form = form_key.get()
            form.form_administrator = group_key
            form.put()

        if not error:
            result = {'success': 'true'}
        else:
            result = {'success': 'false'}

        return self.util.stringify_json(result)


    add = scaffold.add
    view = scaffold.view
    delete = scaffold.delete
