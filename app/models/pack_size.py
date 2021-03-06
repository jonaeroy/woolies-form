from ferris.core.ndb import ndb, BasicModel

class PackSize(BasicModel):
    buyer_or_baa_name = ndb.StringProperty(required=True)
    replenisher = ndb.StringProperty(required=True)
    viewer = ndb.StringProperty(required=False)
    reason_for_change = ndb.StringProperty(required=True)
    department = ndb.StringProperty(required=True)
    supplier_number = ndb.StringProperty(required=True)
    submission_date = ndb.StringProperty(required=True)
    supplier_name = ndb.StringProperty(required=True)
    effective_date = ndb.StringProperty(required=True)
    dsd_or_dc = ndb.StringProperty(required=False)
    details = ndb.TextProperty(required=False)
    notes = ndb.TextProperty(required=False)

    item_number = ndb.StringProperty(required=False)
    item_description = ndb.StringProperty(required=False)
    old_inner = ndb.StringProperty(required=False)
    old_outer = ndb.StringProperty(required=False)
    new_inner = ndb.StringProperty(required=False)
    new_outer = ndb.StringProperty(required=False)
    comments = ndb.StringProperty(required=False)
    attachment = ndb.BlobKeyProperty(required=False)
    status = ndb.IntegerProperty(default=1)
