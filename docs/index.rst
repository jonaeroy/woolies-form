.. toctree::
  :hidden:
  :maxdepth: 2

  getting_started
  tutorial/1_introduction
  users_guide/index

Welcome to The Ferris Framework
===============================

Ferris is rapid application framework created specifically for Google App Engine. Ferris was designed to get you up and running as quickly as possible with flexible, granular scaffolding for common CRUD operations. Ferris is inspired by Ruby on Rails, CakePHP, Django, and Flask.

Ferris is licensed under the `Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

Features
--------
* Uses native App Engine libraries for data modeling.
* Familiar model-view-whatever style architecture.
* Automatic routing with the ability to specify completely custom routes.
* Granular and flexible handler and template scaffolding.
* Powerful template and theme engine built on `Jinja2 <http://jinja.pocoo.org/>`_.
* Integration with `wtforms <http://wtforms.simplecodes.com/>`_.
* Global (application-wide) and local (within object) events system.
* Plugin architecture.
* OAuth2 consumer support built-in.
* Pre-packaged Google API Client, GData Client, and PyTZ for App Engine.


A Quick Look
------------

A simple blog application could be written like this::

    from ferris.core.ndb import BasicModel, ndb
    from ferris.core.easy_handler import EasyHandler, scaffold

    class Post(BasicModel):
        title = ndb.StringProperty()
        content = ndb.TextProperty()

    @scaffold
    class Posts(EasyHandler):
        Model = Post

At this point, a full administrative interface for creating Posts would be available at ``/admin/posts`` and a publicly accessable list and view would be present at ``/posts``.


Documentation
=============

#. :doc:`getting_started` walks you through getting up and running with Ferris.
#. :doc:`tutorial/1_introduction` example shows you how to create your first application.
#. :doc:`users_guide/index` has detailed usage documentation.


Indexes
=======

If you can't find the information you're looking for, have a look at the
index of try to find it using the search function:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



