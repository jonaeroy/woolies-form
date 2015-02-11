from ferris.core.ndb import ndb, BasicModel


class Group(BasicModel):

    name = ndb.StringProperty(required=True)

    @classmethod
    def all(cls):
        return cls.query()

    @classmethod
    def get_group(cls, key):
        return cls.query(cls.key == key)
