from ferris import Behavior
from google.appengine.ext import ndb
from ..models.user import User, UserTag


class CopiesUserTags(Behavior):
    def before_put(self, instance):
        if not ndb.in_transaction() and not instance.user_tags:
            user = User.find_by_user(instance.created_by)
            if user:
                instance.user_tags = user.tags
                instance.user_tag_names = ', '.join([x.get().name for x in instance.user_tags])[:500]
                instance.user_tag_ids = ', '.join([str(x.id()) for x in instance.user_tags])[:500]


class UserTagFields(ndb.Model):
    user_tags = ndb.KeyProperty(UserTag, repeated=True, indexed=False)
    user_tag_names = ndb.StringProperty(indexed=False)
    user_tag_ids = ndb.StringProperty(indexed=False)
