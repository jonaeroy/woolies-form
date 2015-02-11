Testing
=======

.. module:: ferris.tests.lib

Ferris provides utilities to test your application using `nose <>`_ and `webtest <>`_. Ferris provides a few scripts and utility classes to allow you to focus on writing tests instead of worrying about mocking App Engine.

Running Tests
-------------

To run tests you can use the ``backend_test.sh`` (or ``backend_test.bat``)::

    scripts #> ./backend_test.sh

This script will invoke the test runner and discover all tests under ``app/tests`` and run them.

Alternatively, you can run ``ferris/scripts/test_runner.py`` to run the tests::

    ferris/scripts #> python test_runner.py app


Writing Tests for Models
------------------------

Models and other parts of the application that don't involve WSGI (such as services) can be tested using ``WithTestBed``:d

.. autoclass:: WithTestBed

Here is a trivial example::

    from app.models.cat import Cat
    from ferris.tests.lib import WithTestBed

    class CatTest(WithTestBed):
        test_herding(self):
            Cat(name="Pickles").put()
            Cat(name="Mr. Sparkles").put()

            assert Cat.query().count() == 2


Writing Tests for Handlers
--------------------------

Handlers, components, and templates usually have to be tested within a full WSGI environment. This is where ``AppTestCase`` comes in handy:

.. autoclass:: AppTestCase

This allows you to make requests to your application just as you would if the application were running::

    from ferris.tests.lib import AppTestCase

    class CatsTest(AppTestCase):
        test_herding(self):
            Cat(name="Pickles").put()
            Cat(name="Mr. Sparkles").put()

            r = self.testapp.get('/cats')

            assert "Pickles" in r
            assert "Mr. Sparkles" in r
