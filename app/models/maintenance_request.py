from ferris.core.ndb import ndb, BasicModel


class MaintenanceRequest(BasicModel):
    dc = ndb.StringProperty(required=True)
    to = ndb.StringProperty(required=True)
    cc = ndb.StringProperty(required=False)
    warehouse_location = ndb.StringProperty()
    requestor_name = ndb.StringProperty(required=True)
    date_time = ndb.StringProperty(required=True)
    department = ndb.StringProperty(required=True)
    notes = ndb.StringProperty(required=True)
    attachment = ndb.BlobKeyProperty(required=False)
    priority = ndb.StringProperty(required=True)
    
    status = ndb.IntegerProperty(default=1)
