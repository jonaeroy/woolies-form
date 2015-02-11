from ferris.core import time_util, settings
import datetime


def test_localize():
    settings.defaults({'timezone': {
        'local': 'US/Eastern'
    }})

    now = datetime.datetime.now()
    localized = time_util.localize(now)

    assert localized.tzinfo
    assert str(localized.tzinfo) == str(time_util.local_tz())
