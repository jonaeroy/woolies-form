from ferris.core.ndb import ndb, BasicModel

class MultipleChange(BasicModel):
    requestor_name = ndb.StringProperty(required=True)
    reason_for_change = ndb.StringProperty(required=True)
    dc_agreement = ndb.StringProperty(required=True)
    department_name = ndb.StringProperty(required=True)
    supplier_site_number = ndb.StringProperty(required=True)
    passed_business_rules = ndb.StringProperty(required=True)
    submission_date = ndb.StringProperty(required=True)
    supplier_name = ndb.StringProperty(required=True)
    effective_date = ndb.StringProperty(required=True)

    item_number = ndb.StringProperty(required=False)
    item_description = ndb.StringProperty(required=False)
    intent_v_domestic = ndb.StringProperty(required=False)
    old_som = ndb.StringProperty(required=False)
    new_som = ndb.StringProperty(required=False)
    buyer = ndb.StringProperty(required=False)
    sps = ndb.StringProperty(required=False)
    outer_pack = ndb.StringProperty(required=False)
    ti = ndb.StringProperty(required=False)
    hi = ndb.StringProperty(required=False)
    weight = ndb.StringProperty(required=False)
    order_point = ndb.StringProperty(required=False)
    pallet_quantity = ndb.StringProperty(required=False)
    comments = ndb.TextProperty(required=False)

    details = ndb.TextProperty(required=True)

    status = ndb.IntegerProperty(default=1)
