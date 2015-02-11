from ferris.core.ndb import ndb, BasicModel

class BwsStore(BasicModel):
    new_changes_closures = ndb.StringProperty(required=False)

    store_number = ndb.StringProperty(required=True)
    store_name = ndb.StringProperty(required=True)
    effective_date = ndb.StringProperty(required=True)
    state = ndb.StringProperty(required=True)
    banner = ndb.StringProperty(required=False)
    area = ndb.StringProperty(required=True)
    address = ndb.StringProperty(required=False)
    phone_number = ndb.StringProperty(required=False)
    fax_number = ndb.StringProperty(required=False)
    manager_name = ndb.StringProperty(required=False)
    status = ndb.IntegerProperty(default=1)

    trading_hour_monday_open = ndb.StringProperty(required=False)
    trading_hour_tuesday_open = ndb.StringProperty(required=False)
    trading_hour_wednesday_open = ndb.StringProperty(required=False)
    trading_hour_thursday_open = ndb.StringProperty(required=False)
    trading_hour_friday_open = ndb.StringProperty(required=False)
    trading_hour_saturday_open = ndb.StringProperty(required=False)
    trading_hour_sunday_open = ndb.StringProperty(required=False)

    trading_hour_monday_close = ndb.StringProperty(required=False)
    trading_hour_tuesday_close = ndb.StringProperty(required=False)
    trading_hour_wednesday_close = ndb.StringProperty(required=False)
    trading_hour_thursday_close = ndb.StringProperty(required=False)
    trading_hour_friday_close = ndb.StringProperty(required=False)
    trading_hour_saturday_close = ndb.StringProperty(required=False)
    trading_hour_sunday_close = ndb.StringProperty(required=False)

    channel = ndb.StringProperty(required=False)
    merch_state = ndb.StringProperty(required=False)
    company = ndb.StringProperty(required=False)

    other = ndb.TextProperty(required=False)
