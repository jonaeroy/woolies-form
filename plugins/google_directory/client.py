import httplib2
from google.appengine.ext import deferred
from apiclient.discovery import build
from ferris.core.memcache import cached_by_args
from ferris import settings
from plugins import service_account
import logging
import threading
import math
import ndb_cache
from .retries import apply_retry_policy


config = settings.get('google_directory')
USE_BACKENDS = config.get('use_backend', False)
BACKEND_NAME = config.get('backend_name')
DEFAULT_LIMIT = config.get('limit', 30)


scopes = (
    'https://www.googleapis.com/auth/admin.directory.group.readonly',
    'https://www.googleapis.com/auth/admin.directory.user.readonly',
    'https://www.googleapis.com/auth/admin.directory.orgunit.readonly')


def build_client():
    http = httplib2.Http()
    credentials = service_account.build_credentials(scopes)
    credentials.authorize(http)
    return http


@apply_retry_policy
def _get_all_users_inner(directory, param):
    response = directory.users().list(**param).execute()
    return response


def get_all_users():
    result = []
    directory = build('admin', 'directory_v1', http=build_client())
    page_token = None
    param = {
        'maxResults': '100'
    }

    directory_settings = settings.get('google_directory', {
        'domain': service_account.get_config()['domain'],
        'customer': 'C00phkzvz'
    })

    if 'customer' in directory_settings:
        param['customer'] = directory_settings['customer']
    else:
        param['domain'] = directory_settings['domain']

    while True:
        try:
            if page_token:
                param['pageToken'] = page_token

            response = _get_all_users_inner(directory, param)

            for user in response['users']:
                result.append(dict(
                    (k, v) for k, v in user.iteritems()
                    if k in ('orgUnitPath', 'primaryEmail', 'name', 'thumbnailPhotoUrl', 'id', 'isAdmin')
                ))

            page_token = response.get('nextPageToken')

            if not page_token:
                break

            del response

        except Exception as error:
            logging.error(error)
            return False

    return result


def get_user_by_email(email):
    directory = build('admin', 'directory_v1', http=build_client())
    try:
        user = directory.users().get(userKey=email).execute()
        return user
    except Exception as e:
        logging.error('google_directory: Error while retrieving user %s, %s' % (email, e))
        return None


def get_all_groups(user_email=None):
    directory = build('admin', 'directory_v1', http=build_client())
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if user_email is not None:
                param['userKey'] = user_email
            if user_email is None:
                param['domain'] = service_account.get_config()['domain']
            if page_token:
                param['pageToken'] = page_token
            response = directory.groups().list(**param).execute()
            result.extend(response['groups'])
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            logging.error(e)
            break
    return result


def get_group_by_email(email):
    directory = build('admin', 'directory_v1', http=build_client())
    response = directory.groups().get(groupKey=email).execute()
    return response


def get_group_members(group_id):
    directory = build('admin', 'directory_v1', http=build_client())
    response = directory.members().list(groupKey=group_id).execute()
    return response


def get_user_info(email):
    user = get_user_by_email(email)
    if not user:
        return None

    user['groups'] = get_all_groups(email)

    return user


# Cached variations
cache_period = 12 * 60 * 60  # 12 hours

_local_cache = threading.local()

def get_user_info_cached(email):
    if not hasattr(_local_cache, 'users'):
        _local_cache.users = {}
    if email in _local_cache.users:
        return _local_cache.users[email]
    res = get_user_info_cached_impl(email)
    _local_cache.users[email] = res
    return res


get_all_users_cached = ndb_cache.ndb_cached('users', get_all_users, impl=ndb_cache.ndb_sharded_cached_impl, _target=BACKEND_NAME)
get_user_by_email_cached = cached_by_args('domain-groups-list', 12 * 60 * 60)(get_user_by_email)
get_all_groups_cached = cached_by_args('domain-groups-list', 12 * 60 * 60)(get_all_groups)
get_groups_list_cached = ndb_cache.ndb_cached('groups', get_all_groups, impl=ndb_cache.ndb_sharded_cached_impl, _target=BACKEND_NAME)
get_group_by_email_cached = cached_by_args('domain-group', 12 * 60 * 60)(get_group_by_email)
get_group_members_cached = cached_by_args('domain-groups-members', 12 * 60 * 60)(get_group_members)
get_user_info_cached_impl = cached_by_args('domain-user-info', 12 * 60 * 60)(get_user_info)


def prime_caches():
    ndb_cache.refresh('users', get_all_users, impl=ndb_cache.ndb_sharded_cached_impl, _target=BACKEND_NAME)
    ndb_cache.refresh('groups', get_all_groups, impl=ndb_cache.ndb_sharded_cached_impl, _target=BACKEND_NAME)
