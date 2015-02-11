Getting Started With Ferris
===========================

Prerequisites
-------------

Ferris has very few dependencies because it relies on included App Engine libraries and bundles everything else. Just make sure you have the latest Google App Engine SDK for Python installed.

If you want take advantage of unit testing, you'll need to install the following python packages:

 * `unittest2 <http://pypi.python.org/pypi/unittest2>`_
 * `nose <https://nose.readthedocs.org/en/latest/>`_
 * `webob <http://webob.org/>`_
 * `webtest <http://webtest.pythonpaste.org/en/latest/>`_
 * `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_ (optional)

These packages can be easily installed with `pip <http://www.pip-installer.org/en/latest/>`_::

    sudo pip install unittest2 nose webob webtest beautifulsoup


Getting a copy of Ferris
------------------------

The latest version of Ferris can be always be obtained from `Bitbucket <https://bitbucket.org/cloudsherpas/ferris-framework>`_. You can either use git to clone Ferris or download a copy of the master branch. Either way you do it, place the contents of the Ferris' source into the directory where you will be creating your application.


Configuration
-------------

A little bit of configuration has to be done. Open up ``./app.yaml`` and set the application and version properties appropriately, like below::

    application: ferris-getting-started    #.appspot.com
    version: 1

You'll want to pick a unique application name in case you want to actually deploy this. For more information, check out the App Engine documentation.

If you wish to use OAuth2 or Email, you'll also need to change some settings in ``./settings.py`` or use the Settings plugin.

Running with the App Engine development server
----------------------------------------------

Using the development server with a Ferris application is the same as using it with any other App Engine applications. Just issue ``dev_appserver.py .`` on *nix or use the `launcher <https://developers.google.com/appengine/training/intro/gettingstarted#starting>`_ on Windows/Mac. Once it's started you should be able to open up your app via http://localhost:8080. You should see a rather generic landing page.

.. note::
    If you're using the launcher, your URL may be slightly different. Make note of this as the tutorial and examples all use http://localhost:8080.
