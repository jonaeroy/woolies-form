from ferris.tests.lib import AppTestCase


class SanityTest(AppTestCase):

    def testRoot(self):
        self.loginUser()
        resp = self.testapp.get('/')

        self.loginUser(admin=True)
        resp = self.testapp.get('/admin')
        self.assertTrue('Ferris' in resp)
