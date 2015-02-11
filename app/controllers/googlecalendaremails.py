from ferris import Controller, route, route_with
from ferris.core import mail
from ..models.googlecalendaremail import Googlecalendaremail
from app.models.channel import Channel
from ..controllers.utils import Utils
from google.appengine.api import taskqueue
from plugins import directory
import logging
from google.appengine.api import memcache
import urllib, json, os, sys, datetime
from ferris.core import settings
from plugins import calendar


class Googlecalendaremails(Controller):

    @classmethod
    def get_calendar_email_task(self):
        q = taskqueue.Queue('default')
        q.purge()

        taskqueue.add(url='/googlecalendar/get/email', method='GET')
        return 200

    @classmethod
    def get_calendar_email(self):

        # user_list = directory.get_all_users();        
        # logging.info("USER STRING LENGTH =====> %s", len(user_list))
        # logging.info('DIRECTORY USER LIST =================> ' + str(self.util.stringify_json(user_list)))

        result = Googlecalendaremail.query()
        
        for item in result:
            cal_email = item.Calendar_Email
            logging.info('CALENDAR E-MAIL ================>' + str(cal_email))
            self.watch_request_by_email(cal_email)

        return 200

    @classmethod
    def watch_request_by_email(self, email):

        logging.info('EMAIL VALUE BEFORE FILTER ===============> '+ str(email))
        c_db = Channel.find_by_properties(email=email)
        #c_db = Channel.query().filter(Channel.email == str(email))
        logging.info('FIND CHANNEL BY EMAIL ===============> '+ str(c_db))
        if c_db:
            try:
                logging.info(' ===============> TRY STOP WATCH REQUEST')
                self.stop_watch_request(email, c_db.id, c_db.resourceId)
                logging.info('STOP WATCH REQUEST EXECUTED: CALENDAR E-MAIL INFO ===============> '+ str(email))
            except:
                logging.info('===============>  EXCEPTION: STOP WATCH REQUEST EXECUTION')
                pass

        import uuid
       
        uuid = str(uuid.uuid1())

        domain = settings.get('app_config')['PROD_URL']
        post = {
                "id" : uuid,
                "type" : "web_hook",
                "address" : domain + "notifications",
                #"token" : token,\
                "params" :  {
                    "ttl": 10800
                }
            }

        logging.info(' POST ==================>' + str(post))

        channel = calendar.make_watch_request(email, post)

        logging.info(' CHANNEL ==================>' + str(channel))

        try:
            if channel['kind']:
                c_db = Channel.find_by_properties(email=email)
                #c_db = Channel.query().filter(Channel.email == str(email))

                if not c_db:
                    logging.info('===============>  NO CHANNEL FOR THIS EMAIL: CREATING NEW')
                    new_channel = Channel(kind = channel['kind'],
                            id = channel['id'],
                            email= email,
                            uuid = uuid,
                            resourceId = channel['resourceId'],
                            resourceUri = channel['resourceUri'],
                            expiration = channel['expiration'])
                    new_channel.put()

                else:
                    logging.info('===============>  UPDATING CHANNEL FOR THIS EMAIL')
                    c_db.id = channel['id']
                    c_db.resourceId = channel['resourceId']
                    c_db.expiration = channel['expiration']
                    c_db.put()

            return 200
        except:
            logging.info('===============>  EXCEPTION: CHANNEL CREATE/UPDATE')
            pass
            
    @classmethod
    def get_all_modified_events(self, email, updatedMin):
        events = calendar.get_all_modified_events(email, updatedMin)
        return events

    @classmethod
    def stop_watch_request(self, email, id, resourceId):
        post = {
                "id" : str(id),
                "resourceId" : str(resourceId)
                }
        calendar.stop_watch_request(email, post)

    @route_with(template='/stop/watch_request/<email>/<id>/<resourceId>')
    def stop_watch_req(self, email, id, resourceId):
        post = {
                "id" : str(id),
                "resourceId" : str(resourceId)
                }

        stopvar = calendar.stop_watch_request(email, post)
        logging.info('CALENDAR STOP REQUEST ====================> ' + str(stopvar))

    @classmethod
    def save_last_sync(self, cal_email_entity):
        d = datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
        cal_email_entity.last_sync = str(d.isoformat("T") + "Z")
        cal_email_entity.put()
        #self.watch_request_by_email(cal_email_entity.Calendar_Email)


    def process_notifications(self, channel_id, message_number, resource_id, resource_state, resource_uri, channel_expiration, channel_token):

        logging.info("====================process notification=======================")
        logging.info("resource_state : %s channel_id=%s message_number=%s resource_uri=%s channel_expiration=%s channel_token=%s" 
            % (resource_state, channel_id, message_number, resource_uri, channel_expiration, channel_token))

        if resource_state == 'exists':
            logging.info('Resource ID : %s' % (resource_id))
            channel = Channel.query().filter(Channel.id==channel_id).get()

            if channel:

                cal_email_entity = Googlecalendaremail.query().filter(Googlecalendaremail.Calendar_Email==channel.email).get()

                self.save_last_sync(cal_email_entity)

                google_events = self.get_all_modified_events(cal_email_entity.Calendar_Email, cal_email_entity.last_sync)

                logging.info('GOOGLE EVENT CONTENT ===================> ' + str(google_events))

                for _iter in google_events['items']:

                    user_email = _iter['organizer']['email']

                    try:
                        start_datetime = _iter['start']['dateTime']
                        end_datetime = _iter['end']['dateTime']
                        isDateTime = True
                    except:
                        start_datetime = _iter['start']['date']
                        end_datetime = _iter['end']['date']
                        fmt = '%Y-%m-%d'
                        end_datetime = datetime.datetime.strptime(str(end_datetime), fmt).date()
                        end_datetime = end_datetime - datetime.timedelta(days=1)
                        end_datetime = end_datetime.strftime(fmt)
                        isDateTime = False

                    logging.info('START DATE BEFORE CONVERSION ===================> ' + str(start_datetime))
                    logging.info('END DATE BEFORE CONVERSION ===================> ' + str(end_datetime))
                    logging.info('IS DATE ? ===================> ' + str(isDateTime))

                    calUID_key = 'calUID_' + str(_iter['iCalUID'])
                    organizer_key = 'org_email_' + str(_iter['organizer']['email'])
                    calUID = memcache.get(calUID_key)
                    organizer = memcache.get(organizer_key)

                    if calUID is None and organizer is None:

                        memcache.add(key=calUID_key, value=_iter['iCalUID'], time=60)
                        memcache.add(key=organizer_key, value=_iter['organizer']['email'], time=60)
                        self.send_mail_notif(user_email, start_datetime, end_datetime, isDateTime)
        else:
            pass

        return 200

    @classmethod
    def send_mail_notif(self, user_email, start_datetime, end_datetime, isDateTime):
        
        logging.info('===================> INSIDE SEND MAIL')

        if isDateTime:
            start_datetime = str(start_datetime).replace('T', ' ')
            start_datetime = str(start_datetime).translate(None, 'Z')
            end_datetime = str(end_datetime).replace('T', ' ')
            end_datetime = str(end_datetime).translate(None, 'Z')

            conv_sdate = Utils.localize_datetime(start_datetime)
            conv_edate = Utils.localize_datetime(end_datetime)

        else:
            conv_sdate = Utils.localize_date(start_datetime)
            conv_edate = Utils.localize_date(end_datetime)

        logging.info('START DATE ===================> ' + str(start_datetime))
        logging.info('END DATE ===================> ' + str(end_datetime))

        to = user_email
        subject = 'Pool Car Booking Calendar Notification'
        #domain = 'cs-woolies-forms.appspot.com'
        #domain = 'quality-woolies-forms.appspot.com'
        #domain = 'woolworths-forms.appspot.com'

        msg_body = """\
            <html>
            <body>
                Hi %s,
                <br/>
                <br/>
                Here's the link for Woolworths <a href='http://woolworths-forms.appspot.com/poolcarbooks/poolcarbookform?sdate=%s&edate=%s'><b>Pool Car Booking Form </b></a>
                <br/>
                <br/> <i>This is an auto-generated e-mail. Please don't reply.</i>
            </body>
            </html>
        """ % (user_email,conv_sdate,conv_edate)

        mail.send(to, subject, msg_body, str(user_email))

    @route
    def dummy_add(self):

        _list = ['woolworths.com.au_4e534f2d6e706f6f6c76656869636c6531@resource.calendar.google.com', 
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6532@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6533@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6534@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6535@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6536@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6537@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6538@resource.calendar.google.com',
                 'woolworths.com.au_4e534f2d6e706f6f6c76656869636c6539@resource.calendar.google.com'
                 ]
        
        # _list = ['testaccount3@sherpademo.com', 'testaccount4@sherpademo.com', 'testaccount5@sherpademo.com']

        # _list = ['formapprover1@woolworths.com.au', 'formapprover2@woolworths.com.au']

        for value in _list:
            save = Googlecalendaremail(Calendar_Email = value)
            save.put()

        return 200