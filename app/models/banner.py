from ferris.core.ndb import ndb, BasicModel


class Banner(BasicModel):
    url = ndb.StringProperty(required=True)
    display_text = ndb.StringProperty(required=True)
    description = ndb.TextProperty(required=True)
    category = ndb.StringProperty(required=True)

    @classmethod
    def get_all(cls):
        return cls.query().order(cls.category).fetch()

    @classmethod
    def get_category(cls, category):
        return cls.query().filter(cls.category == category).order(cls.category).fetch()
