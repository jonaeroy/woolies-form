from app.etc import search_tools
from ferris import Controller, route, scaffold, messages, route_with
from ferris.components import upload, search
from ..models.user import User, UserTag, UserForm
from ..components.user import User as UserComponent
from plugins.sortable_search import SortableSearch
from google.appengine.api import users

try:
    from plugins import directory
except ImportError as e:
    import logging
    logging.error(e)
    directory = None


class Users(Controller):
    class Meta:
        prefixes = ('admin', 'api')
        components = (scaffold.Scaffolding, upload.Upload, search.Search, UserComponent, SortableSearch, messages.Messaging)

        def set_cache(self):
            self._controller.response.cache_control.no_cache = None
            self._controller.response.cache_control.public = True
            self._controller.response.cache_control.max_age = 600

    class Scaffold:
        ModelForm = UserForm
        display_properties = ('user', 'role')

    def list(self):
        self.scaffold.display_properties = ['name', 'role', 'tags', 'created']
        self.context['sortable'] = ('user', 'role')
        query = self.request.params.get('query', None)
        search_tools.sortable_filtered_search(
            self,
            fields=self.scaffold.display_properties,
            index='auto_ix_User',
            extra_filter="NOT role:Normal" if query is None else None)
        self.context['titles_'] = {
            'name': 'user_name',
            'created': 'created_date',
            'tags': 'group'}

    view = scaffold.view

    @route
    def picture(self, key):
        user = self.util.decode_key(key).get()
        if user.picture:
            return self.redirect(self.uri('download', blob=user.picture))
        else:
            return self.redirect('/plugins/users/img/person.png')

    @route
    def api_me(self):
        self.context['data'] = User.get_current_user()

    @route
    def api_info(self, email):
        self.context['data'] = User.find_or_create_by_user(users.User(email=email))

        self.meta.set_cache()

    @route
    def api_domain(self):
        if not directory:
            return 204

        self.meta.change_view('json')
        self.components.messaging.transform = False

        query = self.request.params.get('q')

        users = directory.get_all_users_cached()

        if query is not None:
            query = query.lower()
            users = filter(
                lambda x: query in x['name'].lower() or query in x['email'].lower(),
                users)

        self.context['data'] = users

        self.meta.set_cache()

    @route
    def api_domain_groups(self):
        if not directory:
            return 204

        self.meta.change_view('json')
        self.components.messaging.transform = False

        self.context['data'] = directory.get_groups_cached()

        self.meta.set_cache()

    @route
    def api_domain_users_and_groups(self):
        if not directory:
            return 204

        self.meta.change_view('json')
        self.components.messaging.transform = False

        query = self.request.params.get('q')

        users = directory.get_all_users_cached()
        groups = directory.get_groups_cached()

        users.extend([{'name': key, 'email': val} for key, val in groups.iteritems()])

        if query is not None:
            query = query.lower()
            users = filter(
                lambda x: query in x['name'].lower() or query in x['email'].lower(),
                users)

        self.context['data'] = users

        self.meta.set_cache()

    @route
    def api_domain_info(self, user_or_group):
        if not directory:
            return 204

        self.meta.change_view('json')
        self.components.messaging.transform = False

        users = directory.get_all_users_cached()
        info = None

        for i in users:
            if i['email'] == user_or_group:
                info = i
                break

        if not info:
            groups = directory.get_groups_cached()
            for name, idx in groups.iteritems():
                if idx == user_or_group:
                    info = {'name': name, 'email': idx}

        if not info:
            return 404

        self.context['data'] = info

        self.meta.set_cache()

    admin_list = list

    admin_add = scaffold.add
    admin_edit = scaffold.edit
    admin_delete = scaffold.delete

    @route
    def api_tags(self):
        self.components.messaging.transform = False
        self.meta.change_view('json')
        query = self.request.params.get('q', '').lower()
        tags = UserTag.query().fetch()

        tags = [x for x in tags if query in x.name.lower()]

        self.context['data'] = tags
        del self.context['user']  # wtf hacks
