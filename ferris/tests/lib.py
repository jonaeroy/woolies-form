from google.appengine.ext import testbed, deferred
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub
from google.appengine.datastore import datastore_stub_util
from google.appengine.api.search.simple_search_stub import SearchServiceStub
from webapp2 import WSGIApplication
import unittest
import webtest
import os
import base64


class TestbedWithFiles(testbed.Testbed):
    def init_blobstore_stub(self):
        import tempfile
        blob_storage = file_blob_storage.FileBlobStorage(tempfile.gettempdir(),
                                                testbed.DEFAULT_APP_ID)
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        self._register_stub('blobstore', blob_stub)
        self._register_stub('file', file_stub)


class WithTestBed(unittest.TestCase):
    """
    Provides a complete App Engine test environment.
    """
    def setUp(self):
        import ferris

        self.testbed = TestbedWithFiles()

        self.testbed.setup_env(
            AUTH_DOMAIN='example.com',
            APPLICATION_ID='_')

        self.testbed.activate()
        self.testbed.init_memcache_stub()

        policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        self.testbed.init_datastore_v3_stub(consistency_policy=policy)
        self.testbed.init_taskqueue_stub(root_path=os.path.join(os.path.abspath(os.path.dirname(ferris.__file__)), '..'))
        self.testbed.init_blobstore_stub()
        self.testbed.init_images_stub()
        self.testbed.init_logservice_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_user_stub()

        stub = SearchServiceStub()
        self.testbed._register_stub('search', stub)

        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def loginUser(self, email='test@example.com', admin=False):
        self.testbed.setup_env(
            USER_EMAIL=email,
            USER_ID='123',
            USER_IS_ADMIN='1' if admin else '0',
            AUTH_DOMAIN='gmail.com',
            overwrite=True)

    def runDeferredTasks(self, queue='default'):
        tasks = self.taskqueue_stub.GetTasks(queue)
        while tasks:
            self.taskqueue_stub.FlushQueue(queue)
            for task in tasks:
                deferred.run(base64.b64decode(task['body']))
            tasks = self.taskqueue_stub.GetTasks(queue)


class AppTestCase(WithTestBed):
    """
    Provides a complete App Engine test environment and also automatically routes all application and plugin handlers to ``testapp``.
    """
    def setUp(self):
        super(AppTestCase, self).setUp()

        import main
        reload(main)
        self.testapp = webtest.TestApp(main.app)


class FerrisTestCase(WithTestBed):
    def setUp(self):
        super(FerrisTestCase, self).setUp()
        app = WSGIApplication(debug=True, config={
            'webapp2_extras.sessions': {'secret_key': 'notasecret'}
        })
        self.testapp = webtest.TestApp(app)

    def addController(self, c):
        c._build_routes(self.testapp.app.router)
