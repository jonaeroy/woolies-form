from ferris.core.ndb import ndb, BasicModel


class BannerCategory(BasicModel):

    name = ndb.StringProperty(required=True)

    @classmethod
    def get_all(cls):
        return cls.query()

    @classmethod
    def get_category(cls, key):
        return cls.query(cls.key == key).fetch()