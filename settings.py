from ferris import settings
from google.appengine.api import app_identity
defaults = {}

defaults['timezone'] = {
    'local': 'Australia/Sydney'
}

defaults['email'] = {
    # Configures what address is in the sender field by default.
    'sender': 'notifications@' + str(app_identity.get_application_id()) + '.appspotmail.com'
}

defaults['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': '1dab62c0-ab88-11e3-a5e2-0800200c9a66',
    },
    #'PROD_URL': 'https://cs-woolies-forms.appspot.com/'
    #'PROD_URL': 'https://quality-woolies-forms.appspot.com/'
    'PROD_URL': 'https://woolworths-forms.appspot.com/'
}

defaults['oauth2'] = {
    # OAuth2 Configuration should be generated from
    # https://code.google.com/apis/console
    'client_id': '655857045283.apps.googleusercontent.com',  # XXXXXXXXXXXXXXX.apps.googleusercontent.com
    'client_secret': 'qdSrnzckZf6YONg6kuUSxXQq'
}

# This enables the template debugger.
# It is automatically disabled in the live environment as it may leak sensitive data.
# Users in the 'required_domain' may view the debugger in the live environment.
defaults['ed_rooney'] = {
    'enabled': True,
    'required_domain': 'cloudsherpas.com'
}

defaults['google_directory'] = {
    'customer': 'C00phkzvz'
}

settings.defaults(defaults)
