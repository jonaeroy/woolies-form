from ferris import messages

class DasboardMessage(messages.Message):
    title = messages.StringField(1)
    route = messages.StringField(2)
    user_isFormApprover = messages.BooleanField(3, default=False)
    user_isFormAdmin = messages.BooleanField(4, default=False)
    user_directory_givenName = messages.StringField(5)
    user_directory_fullname = messages.StringField(6)
    user_email = messages.StringField(9)
    
    #forms = messages.MessageField(Form, 9, repeated=True)
    
class Form(messages.Message):
    name = messages.StringField(1)
    list_url = messages.StringField(2)
    add_url = messages.StringField(3)

