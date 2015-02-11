"""
OAuth dance session
"""

from google.appengine.ext import ndb
from ferris.core.ndb import Model
from credentials_property import CredentialsProperty
from ndb_storage import NdbStorage


class UserCredentials(Model):

    user = ndb.UserProperty()
    scopes = ndb.StringProperty(repeated=True)
    admin = ndb.BooleanProperty()
    credentials = CredentialsProperty()
    filter_scopes = ndb.StringProperty()

    @classmethod
    def _get_kind(cls):
        return '__ferris__oauth2_user_credentials'

    @classmethod
    def after_get(cls, key, item):
        if item and item.credentials:
            item.credentials = NdbStorage(key, 'credentials', item).get()

    def before_put(self):
        if self.scopes:
            self.filter_scopes = ','.join(sorted(self.scopes))

    @classmethod
    def _get_parent_key(cls, user, admin):
        if user and not admin:
            return ndb.Key('oauth2_parent', 'User:%s' % user)
        elif admin:
            return ndb.Key('oauth2_parent', 'Admin')

    @classmethod
    def _find_query(cls, user=None, scopes=None, admin=None):
        parent_key = cls._get_parent_key(user, admin)

        q = cls.query(ancestor=parent_key)

        if scopes:
            scopes = ','.join(sorted(scopes))
            q = q.filter(cls.filter_scopes == scopes)

        if user:
            q = q.filter(cls.user == user)

        return q

    @classmethod
    def create(cls, user, scopes, credentials, admin):
        parent = cls._get_parent_key(user, admin)
        item = cls(parent=parent, user=user, scopes=scopes, credentials=credentials, admin=admin)
        item.put()
        return item

    @classmethod
    def find(cls, user=None, scopes=None, admin=None):
        x = cls._find_query(user, scopes, admin).get()
        if x:
            cls.after_get(x.key, x)
        return x

    @classmethod
    def find_all(cls, user, scopes, admin):
        x = cls._find_query(user, scopes, admin)
        for _ in x:
            cls.after_get(_.key, _)
        return x

    @classmethod
    def delete_all(cls, user, scopes, admin):
        c = cls.find_all(user, scopes, admin)
        for x in c:
            x.key.delete()
