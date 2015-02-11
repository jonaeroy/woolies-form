from ferris.core.ndb import ndb, BasicModel

class Channel(BasicModel):

    kind = ndb.StringProperty(required=True)
    id = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    uuid = ndb.StringProperty(required=True)
    resourceId = ndb.StringProperty(required=True)
    resourceUri = ndb.StringProperty(required=True)
    expiration = ndb.StringProperty(required=True)

    @classmethod
    def all(cls):
        return cls.query()

    @classmethod
    def order_by_email_asc(cls):
        return cls.query().order(cls.email)

    @classmethod
    def order_by_fullname_asc(cls):
        return cls.query().order(cls.fullname)