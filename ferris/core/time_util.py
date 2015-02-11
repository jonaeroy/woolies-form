from pytz.gae import pytz
from . import settings

from dateutil import tz
from datetime import datetime

def utc_tz():
    return pytz.timezone('UTC')


def local_tz():
    return pytz.timezone(settings.get('timezone')['local'])


def localize(dt):
    if not dt.tzinfo:
        dt = utc_tz().localize(dt)
    return dt.astimezone(local_tz())

def localize_datetime(date_time):

    fmt = '%Y-%m-%d %H:%M:%S'
    fmt2 = '%b %d, %Y %I:%M %p'

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')

    utc = datetime.strptime(str(date_time)[:19], fmt)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)

    vardtime = central.strftime(fmt2)

    return vardtime