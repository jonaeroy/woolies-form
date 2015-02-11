from ferris.tests.lib import WithTestBed
from google.appengine.api import users
from ..models.user import User


class UserModelTest(WithTestBed):

    def testCreationByUser(self):
        gae_user = users.User(email="test@example.com")

        user = User.find_or_create_by_user(gae_user)
        user = User.find_or_create_by_user(gae_user)

        assert User.query().count() == 1
