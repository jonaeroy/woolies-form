import httplib2, logging
from apiclient.discovery import build
from plugins import service_account

scopes = (
    'https://www.googleapis.com/auth/calendar.readonly'
    )

def build_client(user):
    http = httplib2.Http()
    credentials = service_account.build_credentials(scopes, user)
    credentials.authorize(http)
    return http

def get_all_events(email):
    response = None
    page_token = None
    while True:
        calendar = build('calendar', 'v3', http=build_client(email))
        param = {'calendarId': email, 'timeZone' : 'GMT', 'singleEvents' : True, 'showDeleted': True, 'pageToken':page_token}
        events = calendar.events().list(**param).execute()

        if not page_token:
            response = events
        else:
            response['items'].extend(events['items'])


        logging.info("google event response ==> %s" % response)

        page_token = events.get('nextPageToken')
        if not page_token:
            break

    return response

def get_all_modified_events(email, updatedMin):
    response = None
    page_token = None
    while True:
        calendar = build('calendar', 'v3', http=build_client('admin.smartin@woolworths.com.au'))
        param = {'calendarId': email, 'timeZone' : 'GMT', 'singleEvents' : True, 'showDeleted': False, 'updatedMin' : updatedMin, 'pageToken':page_token}
        events = calendar.events().list(**param).execute()

        if not page_token:
            response = events
        else:
            response['items'].extend(events['items'])

        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return response

def make_watch_request(email, post):
    calendar = build('calendar', 'v3', http=build_client('admin.smartin@woolworths.com.au'))
    response = calendar.events().watch(calendarId=email, body=post).execute()
    return response

def stop_watch_request(email, post):
    calendar = build('calendar', 'v3', http=build_client(email))
    response = calendar.channels().stop(body=post).execute()
    return response
