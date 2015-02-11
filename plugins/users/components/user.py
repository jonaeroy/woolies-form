from ..models.user import User as UserModel


class User(object):
    def __init__(self, controller):
        self.controller = controller
        self.controller.events.before_startup += self._on_before_startup

    def _on_before_startup(self, *args, **kwargs):
        self.user = UserModel.get_current_user()
        self.controller.context['current_user'] = self.user

    def __call__(self):
        return self.user
