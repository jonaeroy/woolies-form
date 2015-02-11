from ferris.core.ndb import ndb, BasicModel

class TrainingRequest(BasicModel):
    
    to = ndb.StringProperty(required=True)
    employee_number = ndb.StringProperty(required=True)
    email_address = ndb.StringProperty(required=False)
    participant_name = ndb.StringProperty(required=True)
    preferred_training_day = ndb.StringProperty(required=False)
    participant_position_title = ndb.StringProperty(required=False)
    shift_type = ndb.StringProperty(required=False)
    participant_dob = ndb.StringProperty(required=True)
    preferred_training_location = ndb.StringProperty(required=True)
    cost_center_number = ndb.StringProperty(required=True)
    current_cert_exp_date = ndb.StringProperty(required=False)
    participant_mobile_number = ndb.StringProperty(required=False)
    store_site_name = ndb.StringProperty(required=True)
    division = ndb.StringProperty(required=True)

    first_aid = ndb.StringProperty(required=False)
    responsible_service_of_alcohol = ndb.StringProperty(required=False)
    fire_training = ndb.StringProperty(required=False)
    fork_lift = ndb.StringProperty(required=False)
    rehabilitation = ndb.StringProperty(required=False)
    food_safety = ndb.StringProperty(required=False)
    safety = ndb.StringProperty(required=False)

    special_instructions = ndb.TextProperty(required=False)

    status = ndb.IntegerProperty(default=0)
