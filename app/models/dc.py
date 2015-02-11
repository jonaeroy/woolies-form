from ferris.core.ndb import ndb, Model

class Dc(Model):
    location_number = ndb.StringProperty(required=True)
    location_name = ndb.StringProperty(required=True)

    @classmethod
    def get_dcs(cls):
        return cls.query().order(cls.location_number)
