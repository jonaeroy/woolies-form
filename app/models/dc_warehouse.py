from ferris.core.ndb import ndb, Model

class DcWarehouse(Model):
    dc_name = ndb.StringProperty(required=True)
    address = ndb.TextProperty(required=True)
    maintenance_or_dc_manager = ndb.StringProperty(required=True)
    mobile_number = ndb.StringProperty(required=False)
    email_address = ndb.StringProperty(required=True)
    strategy = ndb.StringProperty(required=False)

    @classmethod
    def get_all(cls):
        return cls.query().order(cls.dc_name)