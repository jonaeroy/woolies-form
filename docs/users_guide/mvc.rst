MVC in Ferris
=============

Ferris is similar to a lot of other MVC frameworks, though the terminology is slightly different:

* :doc:`models` handle the retrieval and storage of data in the App Engine Datastore. Models are simply Google App Engine `ndb.Model <https://developers.google.com/appengine/docs/python/ndb/>`_ subclasses with a few helper methods. Typically a most of the business logic is implemented in the model layer.
* :doc:`handlers` are responsible for responding to HTTP requests. Handlers are typically thin glue between models and templates. Handlers have special methods called *actions* that are accessable via HTTP.
* :doc:`templates` handle the presentation of data to the user. Templates have access to data from that's retrived by the handlers. Ferris uses the `jinja2 <http://jinja.pocoo.org/>`_ template engine.
* :doc:`routing` Maps urls to handler actions. This happens more or less automatically, but you can define custom routes and redirects.
* :doc:`scaffolding` can automatically create CRUD (create, read, update, delete) actions and templates for you, and can be customized and augmeneted to fit your needs.
* :doc:`forms` are ways of representing data submitted by a client that's used to update a model.
* :doc:`components` are a way of packaging common handler behavior into reusable classes.
* :doc:`plugins` are a way of packaging entire parts of an application to be reused in another.
