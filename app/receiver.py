import webapp2
import logging
from app.controllers.googlecalendaremails import Googlecalendaremails
from google.appengine.api import memcache


class NotificationReceiver(webapp2.RequestHandler):
    def post(self):
        channel_id = self.request.headers['X-Goog-Channel-ID']
        message_number = self.request.headers['X-Goog-Message-Number']
        resource_id = self.request.headers['X-Goog-Resource-ID']
        resource_state = self.request.headers['X-Goog-Resource-State']
        resource_uri = self.request.headers['X-Goog-Resource-URI']

        try:
            channel_expiration = self.request.headers['X-Goog-Channel-Expiration']
        except:
            channel_expiration = 'null'

        try:
            channel_token = self.request.headers['X-Goog-Channel-Token']
        except:
            channel_token='null'

        Googlecalendaremails().process_notifications(channel_id, message_number, resource_id, resource_state, resource_uri, channel_expiration, channel_token)
            

class GoogleCalGetter(webapp2.RequestHandler):
    def get(self):
        logging.info('==============> INSIDE METHOD')
        Googlecalendaremails.get_calendar_email()

app = webapp2.WSGIApplication([
    ('/notifications', NotificationReceiver),
    ('/googlecalendar/email/task', GoogleCalGetter)
])