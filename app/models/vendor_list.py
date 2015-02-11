from ferris.core.ndb import ndb, Model

class VendorList(Model):
    vendor = ndb.StringProperty(required=True)

    @classmethod
    def get_all(cls):
        return cls.query().order(cls.vendor)