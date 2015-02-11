from string import join
from ferris import cached
from ferris.core.ndb import Model, ndb
from google.appengine.api import blobstore, images, files, users
from ferris.behaviors import searchable
import datetime
import logging


try:
    from plugins import directory
except ImportError:
    directory = None


GROUPS_UPDATE_INTERVAL = 1 * 60 * 60  # once per hour.


class UserGroup(Model):
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class UserTag(Model):
    name = ndb.StringProperty(indexed=True)


class User(Model):
    class Meta:
        behaviors = (searchable.Searchable,)
        search_index = ('auto_ix_User', 'global')

        @staticmethod
        def search_indexer(instance, properties):
            data = searchable.default_indexer(instance, properties)
            data['role'] = instance.role
            data['user'] = instance.user.email()
            data['modified'] = instance.modified
            data['created'] = instance.created
            data['tags'] = join([x.get().name for x in instance.tags],', ')
            # Add relations here
            return data

    name = ndb.StringProperty(indexed=False)
    user = ndb.UserProperty(required=True)
    orgunit = ndb.StringProperty(indexed=False)
    role = ndb.StringProperty(choices=('Normal', 'SME', 'Admin'), default='Normal', indexed=True)
    groups = ndb.LocalStructuredProperty(UserGroup, indexed=False, repeated=True)
    picture = ndb.BlobKeyProperty(indexed=False)
    modified = ndb.DateTimeProperty(auto_now=True, indexed=False)
    created = ndb.DateTimeProperty(auto_now=True, indexed=False)
    is_normal_user = ndb.ComputedProperty(lambda self: self.role == 'Normal', indexed=True)

    tags = ndb.KeyProperty(kind=UserTag, repeated=True)

    @classmethod
    @cached("user.count", 1 * 60 * 60)
    def get_totals(cls):
        return {
            'Admin': cls.query().filter(cls.role == 'Admin').count(),
            'SME': cls.query().filter(cls.role == 'SME').count(),
            'Normal': cls.query().filter(cls.role == 'Normal').count()
        }

    @classmethod
    def find_or_create_by_user(cls, user, role='Normal'):
        if not user:
            return None

        key = ndb.Key('User', user.email())
        result = key.get()

        if not result:
            result = cls(key=key, user=user, role=role)
            result.put()

        result._check_groups()
        return result

    @classmethod
    def get_current_user(cls):
        user = users.get_current_user()
        if not user:
            return None
        return cls.find_or_create_by_user(
            user,
            'Admin' if users.is_current_user_admin() else 'Normal')

    def _check_groups(self):
        """
        Checks if the groups haven't been updated within a certain amount of time.
        If not, it'll update them. The interval can be adjusted at the top
        """
        if self.modified < datetime.datetime.now() - datetime.timedelta(seconds=GROUPS_UPDATE_INTERVAL):
            self.put()

    def before_put(self):
        if not self.key.id():
            self.key = ndb.Key('User', self.user.email())

        user = None
        try:
            if not directory:
                return
            user = directory.get_user_by_email(self.user.email())
        except:
            user = None
        if user is not None:
            self._update_picture()
            self._update_name(user['name'])
            self._update_org_unit(user['orgunit'])
            self._update_groups()

    def _update_name(self, name):
        logging.info(name)
        if not self.name:
            try:
                self.name = name
            except:
                self.name = self.user.nickname()

    def _update_org_unit(self, org_unit):
        if not self.orgunit:
            try:
                self.orgunit = org_unit
            except:
                self.orgunit = None

    def _update_groups(self):
        if not directory:
            return
        try:
            groups = directory.get_all_groups(user_email=self.user.email())
            self.groups = [UserGroup(name=k, email=v) for k, v in groups.iteritems()]
        except:
            pass

    def _update_picture(self):
        if self.picture:
            if self.key.id():
                old = self.key.get(use_cache=False)
                if old.picture != self.picture:
                    if old.picture:
                        blobstore.delete(old.picture)
                    self.crop_picture()
            else:
                self.crop_picture()

    def crop_picture(self):
        image = images.Image(blob_key=self.picture)
        image.resize(width=200)
        data = image.execute_transforms(output_encoding=images.PNG)

        file_name = files.blobstore.create(mime_type='image/png')
        with files.open(file_name, 'a') as f:
            f.write(data)
        files.finalize(file_name)

        self.picture = files.blobstore.get_blob_key(file_name)

    @classmethod
    def before_delete(cls, key):
        self = key.get()
        if self.picture:
            blobstore.delete(self.picture)

    def __unicode__(self):
        return self.name or self.user.nickname() or self.user.email()


from ferris.core.forms import model_form
from wtforms.widgets import TextInput


class UserAutocompleteWidget(TextInput):
    def __init__(self):
        super(UserAutocompleteWidget, self).__init__()

    def __call__(self, field, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = u'%s %s' % ('user-autocomplete', c)
        return super(UserAutocompleteWidget, self).__call__(field, **kwargs)


# Picture is excluded for now.
class UserForm(model_form(User,
    exclude=('groups', 'picture', 'orgunit'),
    field_args={
        'user': {'label': 'Email', 'widget': UserAutocompleteWidget()},
        'tags': {'label': 'Groups'}})):
    pass
