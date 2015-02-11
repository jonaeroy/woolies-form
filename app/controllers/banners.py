from ferris import Controller, scaffold, route
from ..models.banner import Banner
from ferris.components import pagination
from ..models.user import User
from google.appengine.api import users
from ferris.core.ndb import ndb


class Banners(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, pagination.Pagination)
        pagination_limit = 10

    class Scaffold:
        display_properties = ('url', 'display_text', 'description', 'category', 'created_by', 'created')

    delete = scaffold.delete
    # edit = scaffold.edit

    def list(self):
        for key, value in self.session.items():
            self.context[key] = value

        current_user = users.get_current_user().email()
        result = User.get_by_email(current_user)
        record = result.get()

        if record.banner_category:
            record = record.banner_category.get()
            _set = Banner.get_category(record.name)
        else:
            _set = []

        self.context['data'] = _set

    def add(self):
        current_user = users.get_current_user().email()
    
        result = User.get_by_email(current_user)
        record = result.get()
        
        if record.banner_category:
            banner_category = record.banner_category.get()
        else:
            banner_category = None

        self.context['banner_category'] = banner_category

        return scaffold.add(self)

    def edit(self, key):
        self.context['key'] = key

        #Retrieve Record
        record = ndb.Key(urlsafe=key).get()

        self.context['url'] = record.url
        self.context['display_text'] = record.display_text
        self.context['description'] = record.description
        self.context['category'] = record.category

        return scaffold.edit(self, key)

    @route
    def display(self):
        results = Banner.get_all()
        link = {}
        layout = ""

        for result in results:
            if result.category not in link:
                link[result.category] = []
                layout += "<h2>%s</h2>" % result.category

            details = {}
            details['url'] = result.url
            details['description'] = result.description
            details['display_text'] = result.display_text

            layout += "<div class='banner-div'><a href='%s' target='_blank'>%s</a><p>%s</p></div>" % (result.url, result.display_text, result.description)

            link[result.category].append(details)

        # return layout

        self.context['data'] = layout
