OAuth2
======

Ferris provides quite a few helpers for utilizing OAuth2 with the Google APIs. Ferris provides an implementation of the OAuth2 web server flow and exposes the ability to get credentials for particular scopes easily.

.. module:: ferris.components.oauth

Configuration
-------------

In order to use Ferris' OAuth2 features, you must first configure client settings in ``settings.py``::

    app_config['oauth2'] = {
        'client_id': 'XXXXXXXXXXXXXXX.apps.googleusercontent.com'
        'client_secret': 'XXXXXXXXXXXXXXX'
    }

You can generate your own Client ID and Secret at https://code.google.com/apis/console

Example
-------

A quick example of how to use the OAuth2 features to interact with a Google API::

    from ferris.core.handler import Handler
    from ferris.components.oauth import OAuth
    from apiclient.discovery import build

    class Example(Handler):
        components = [OAuth]
        oauth_scopes = ['https://www.googleapis.com/auth/userinfo.profile']

        @oauth.require_credentials
        def list(self):
            http = self.oauth.http()
            service = build('oauth2', 'v2', http=http)

            user_info = service.userinfo().get().execute()

            return self.redirect(str(user_info['picture']))

This example uses the Google user info service to show the user their profile picture. When you first navigate to http://localhost:8080/example, you'll be taken through the entire OAuth Flow. You will only have to complete this once, as it stores the credentials for subsequence requests.


The OAuth Component
-------------------

.. autoclass:: OAuth

As in the example above, to use the component add it to the component list and be sure to specify the needed scopes using the :attr:`oauth_scopes` attribute::

    from ferris.core.handler import Handler
    from ferris.components.oauth import OAuth

    class Example(Handler):
        components = [OAuth]
        oauth_scopes = ['https://www.googleapis.com/auth/userinfo.profile']

You must decorate every action that needs credentials with either ``@require_credentials``, ``@provide_credentials``, or ``@require_admin_credentials``::

    @oauth.require_credentials
    def list(self):
        http = self.oauth.http()

    @route
    @oauth.provide_credentials
    def test(self):
        if not self.oauth.has_credentials():
            return "No credentials"

.. autofunction:: require_credentials

.. autofunction:: provide_credentials

Sometimes you need to use one account for every user, like a service account. You can achieve this using *admin* credentials. These sort of credentials can only be created by an administrator of an application but will be available for all requests to use.

.. autofunction:: require_admin_credentials

Using Credentials
-----------------

Usually you'll want an ``http`` object that's signed with the credentials:

.. automethod:: OAuth.http

You can use this to build a service object::

    http = self.oauth.http()
    service = build('oauth2', 'v2', http=http)

Though, sometimes you want access to the credentials object directly:

.. automethod:: OAuth.credentials

To check if the credentials exist and are valid, you can use:

.. automethod:: OAuth.has_credentials

If you want to request that the user grant you access (if you're using provide instead of require) redirect them to the result of:

.. automethod:: OAuth.authorization_url

