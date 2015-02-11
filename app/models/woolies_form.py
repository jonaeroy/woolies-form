from ferris.core.ndb import ndb, BasicModel
from app.models.group import Group


class WooliesForm(BasicModel):

    name = ndb.StringProperty(required=True)
    list_url = ndb.StringProperty(required=True)
    add_url = ndb.StringProperty(required=True)
    form_administrator = ndb.KeyProperty(Group, indexed=True, repeated=False)
    first_level_manager = ndb.KeyProperty(Group, indexed=True, repeated=False)
    second_level_manager = ndb.KeyProperty(Group, indexed=True, repeated=False)

    @classmethod
    def all(cls):
        return cls.query().order(cls.name)