Components
==========

Components are pieces of functionality that can be invoked by a handler or react to handler events. Components are a great way to re-use code between controllers, such as with pagination, searching, emailing, etc.


Using Components
----------------

Import your desired components and include them in the ``components`` property on your handler, like so::

    from ferris.components.pagination import Pagination
    from ferris.components.json import Json

    class Documents(Handler):
        components = [Pagination, Json]

Inside of your actions, you can access the component instances using ``self.components``::

    def list(self):
        self.components.pagination.paginate()


Built-in Components
-------------------

.. module:: ferris.components

The :mod:`ferris.components` provides a few built-in components. These can be used directly, customized, or used as guidelines when building your own.

Pagination
~~~~~~~~~~

.. autoclass:: ferris.components.pagination.Pagination

.. automethod:: ferris.components.pagination.Pagination.paginate

For example of using this, see :doc:`../tutorial/7_extras`

Email
~~~~~

.. autoclass:: ferris.components.email.Email

.. automethod:: ferris.components.email.Email.send

.. automethod:: ferris.components.email.Email.send_template

For example::

    from ferris.core.handler import Handler
    from ferris.components.email import Email

    class Example(Handler):
        components = [Email]

        def list(self):
            self.set(text="Hello!")
            self.components.email.send_template(
                recipient="test@example",
                subject="Test Email",
                template="emails/test.html")

Assuming you have a template at ``emails/test.html``.


JSON
~~~~

.. autoclass:: ferris.components.json.Json

For example::

    from ferris.core.handler import Handler, scaffold
    from ferris.components.json import Json

    @scaffold
    class Posts(Handler):
        components = [Json]

        @scaffold
        def list(self):
            pass

In this example, making a request to http://localhost:8080/posts will render an HTML template of all posts, but making a request to http://localhost:8080/posts?alt=json will return the list of posts as JSON.


Upload
~~~~~~

The :class:`Upload` component can take the guesswork out of using the  `Blobstore API <https://developers.google.com/appengine/docs/python/blobstore/>`_ to upload binary files. It works with :doc:`forms` and :doc:`models`.

.. autoclass:: ferris.components.upload.Upload

A simple example::

    from ferris.core.ndb import Model, ndb
    from ferris.core.handler import Handler, scaffold
    from ferris.components.upload import Upload

    class Picture(Model):
        file = ndb.BlobKeyProperty()

    @scaffold
    class Pictures(Handler):
        components = [Upload]


Search
~~~~~~

The :class:`Search` component makes it really use to use the `Search API <https://developers.google.com/appengine/docs/python/search/>`_.

In order to use search, you must first :func:`index` your models:

.. autofunction:: ferris.components.search.index

Be sure to unindex when an item is deleted or no longer needed:

.. autofunction:: ferris.components.search.unindex

With documents in the search index you can use the search component:

.. autoclass:: ferris.components.search.Search

.. automethod:: ferris.components.search.Search.search

For example of using this, see :doc:`../tutorial/7_extras`
