from ferris.core.ndb import ndb, BasicModel
from app.models.group import Group
from app.models.banner_category import BannerCategory


class User(BasicModel):

    email = ndb.StringProperty(required=True)
    fullname = ndb.StringProperty(required=True)
    group = ndb.KeyProperty(Group, repeated=True)
    #group = ndb.KeyProperty(Group, indexed=True, repeated=False)
    role = ndb.StringProperty(required=True, choices=set(["None", "Administrator"]))
    banner_category = ndb.KeyProperty(BannerCategory, indexed=True, repeated=False)
    favorites = ndb.TextProperty(default="[]")

    @classmethod
    def all(cls):
        return cls.query()

    @classmethod
    def order_by_email_asc(cls):
        return cls.query().order(cls.email)

    @classmethod
    def order_by_fullname_asc(cls):
        return cls.query().order(cls.fullname)

    @classmethod
    def get_by_email(cls, email):
        return cls.find_all_by_email(email)

    @classmethod
    def create(cls, email, user_fullname):
        instance = cls.query(cls.email == email).get()

        if instance is None:
            instance = cls(email=email, fullname=user_fullname, role='None').put()
            instance = instance.get()

        return instance
