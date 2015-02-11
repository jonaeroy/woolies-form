Models
======

Models are responsible for persisting data and containing application logic.

Conventions
-----------

Models are named with singular nouns (for example: Page, User, Image, Bear, etc.). Breaking convention is okay, but scaffolding will not work properly without some help.

Each model class should be in it's own file under ``/app/models`` and the name of the file should be the underscored class name. For example, to create a model to represent furry bears, you would create the file ``/app/models/furry_bear.py`` and inside of that define a class named ``FurryBear``.

Ferris' Model Class
-------------------

.. module:: ferris.core.ndb

The Model class is built on top of App Engine's ``google.appengine.ext.ndb`` module and there is nothing stopping you from directly using any regular ndb.Model class with Ferris. Documentation on propeties, querying, etc. can be found `here <https://developers.google.com/appengine/docs/python/ndb/>`_.

.. autoclass:: ferris.core.ndb.Model

.. automethod:: ferris.core.ndb.Model.find_all_by_properties

.. automethod:: ferris.core.ndb.Model.find_by_properties

Automatic Methods
-----------------

The Model class automatically generates a ``find_by_[property]`` and a ``find_all_by_[property]`` classmethod for each property in your model.These are shortcuts to the above methods.

For example::

    Show.find_all_by_title("The End of Time")
    Show.find_all_by_author("Russell T Davies")

Callbacks
---------

Additionally the Model class provides aliases for the callback methods. You can override these methods in your Model and they will automatically be called after their respective action.

.. automethod:: ferris.core.ndb.Model.before_put
.. automethod:: ferris.core.ndb.Model.after_put
.. automethod:: ferris.core.ndb.Model.before_get
.. automethod:: ferris.core.ndb.Model.after_get
.. automethod:: ferris.core.ndb.Model.before_delete
.. automethod:: ferris.core.ndb.Model.after_delete

These methods are useful for replicating database triggers, enforcing application logic, validation, search indexing, and more.

Access Fields
-------------

The :class:`BasicModel` adds automatic access fields:

.. autoclass:: ferris.core.ndb.BasicModel

.. py:attribute:: ferris.core.ndb.BasicModel.created

    Stores the created time of an item as a datetime (UTC)

.. attribute:: ferris.core.ndb.BasicModel.modified

    Stores the modified time of an item as a datetime (UTC)

.. attribute:: ferris.core.ndb.BasicModel.created_by

    Stores the user (a ``google.appengine.api.users.User``) who created an item.

.. attribute:: ferris.core.ndb.BasicModel.modified_by

    Stores the user (a ``google.appengine.api.users.User``) who modified an item.

