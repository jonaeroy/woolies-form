from ferris.core import plugins
from ferris.core.events import on
import logging

plugins.register('users')


from .models.user import User as UserModel
from .components.user import User as UserComponent


def get_current_user():
    return UserModel.get_current_user()


@on('controller_before_render')
def controller_before_render(controller):
    user = get_current_user()
    logging.info(user)
    controller.context.set_dotted('plugins.users.user', user)


#Monkey Patch App Engine users

from google.appengine.api.users import User as AppengineUser


def _get_info(self):
    if not hasattr(self, '_user_info'):
        setattr(self, '_user_info', None)
    if not self._user_info:
        self._user_info = UserModel.find_or_create_by_user(self)
    return self._user_info

setattr(AppengineUser, 'info', property(_get_info))
