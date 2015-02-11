from ferris.core.ndb import ndb, BasicModel

class Vendor(BasicModel):
    subject = ndb.StringProperty(required=True)
    cc = ndb.StringProperty(required=True)
    to = ndb.StringProperty(required=True)
    dc = ndb.StringProperty(required=True)
    po_number = ndb.StringProperty(required=True)
    delivery_date = ndb.StringProperty(required=True)
    vendor_number = ndb.StringProperty(required=True)
    vendor_name = ndb.StringProperty(required=True)
    pallets_received = ndb.StringProperty(required=True)
    pallets_affected = ndb.StringProperty(required=True)
    po_rejected = ndb.StringProperty(required=False)
    po_on_woolworths_primary_flight = ndb.StringProperty(required=False)
    issue_raised_in_pct = ndb.StringProperty(required=False)
    notes = ndb.TextProperty(required=False)
    attachment = ndb.BlobKeyProperty(required=False)
    status = ndb.IntegerProperty(default=1)
