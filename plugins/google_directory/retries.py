from apiclient import errors
from time import sleep
import functools
import logging


def retries(max_tries, should_retry, delay=1, backoff=2):
    """Function decorator implementing retrying logic."""
    def dec(func):
        #functools.wraps(func)
        def f2(*args, **kwargs):
            mydelay = delay
            tries = range(max_tries)
            tries.reverse()
            for tries_remaining in tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if tries_remaining > 0 and should_retry(e):
                        sleep(mydelay)
                        mydelay = mydelay * backoff
                    else:
                        raise
                else:
                    break
        return f2
    return dec


def http_retry_policy(exception):
    if not isinstance(exception, errors.HttpError):
        return False
    if exception.resp['status'] in ('400', '401', '402', '403', '404'):
        return False
    return True


def apply_retry_policy(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except errors.HttpError as error:
            logging.warning("May retry: %s" % error)
            raise
        except Exception as error:
            logging.error("Fatal HTTP Error: %s" % error)
            raise

    r_inner = retries(max_tries=5, should_retry=http_retry_policy, delay=1, backoff=2)(inner)
    return r_inner
