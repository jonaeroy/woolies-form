Routing
=======

Ferris will automatically create a route name and url for every action in every handler in your application. You can also specify additional routes using the file ``app/routes.py``.

.. currentmodule:: ferris.core.handler

Parts
-----

Actions in your application are referenced using four parts:

* The name of the handler
* The prefix, if specified
* The name of the action
* The parameters of the action, if any

These are called the *route parts* and are used to build both the route name and the url for a particular action.

URL and Name Generation
-----------------------

For the route name, it follows the convention ``[prefix-]handler-action`` with handler being underscored.

For the url, it follows the convention ``[/prefix]/handler/action[/param_1, etc.]`` with handler being underscored.

The following table demonstrates various mappings:

+-------------------------------+-------------------------------+-------------------------------+
|Action                         | URL                           | name                          |
+===============================+===============================+===============================+
| Time.stop()                   | /time/stop                    | time-stop                     |
+-------------------------------+-------------------------------+-------------------------------+
| Daleks.exterminate(who)       | /daleks/exterminate/<who>     | daleks-exterminate            |
+-------------------------------+-------------------------------+-------------------------------+
| Numbers.range(min, max)       | /numbers/range/<min>/<max>    | numbers-range                 |
+-------------------------------+-------------------------------+-------------------------------+
| Spaceships.xml_specs()        | /xml/spaceships/specs         | xml-spaceships-specs          |
+-------------------------------+-------------------------------+-------------------------------+
| UserComments.json_stats       | /json/user_comments/stats     | json-user_comments-stats      |
+-------------------------------+-------------------------------+-------------------------------+

CRUD Actions
------------

The methods named ``list``, ``view``, ``add``, ``edit``, and ``delete`` are *always* treated as actions and are implicitly routed (even when prefixed).

These methods have preset url mappings as follows, but can be prefixed:

+---------+----------------------+
|Action   | URL                  |
+=========+======================+
|list     |  /handler            |
+---------+----------------------+
|add      |  /handler/add        |
+---------+----------------------+
|view     |  /handler/<id>       |
+---------+----------------------+
|edit     |  /handler/<id>/edit  |
+---------+----------------------+
|delete   |  /handler/<id>/delete|
+---------+----------------------+

Non-CRUD Actions
----------------

Other methods need to be explicitly routed using ``@route`` or ``@route_with``.

Take the following methods for example::

    def list(self):
        return 'list'

    @route
    def test(self):
        return 'test'

    def run(self):
        return 'run'

The methods ``list`` and ``test`` will be accessible via HTTP, but the method ``run`` is only accessible from code.

.. autofunction:: ferris.core.handler.route

To set a custom url for an action, use ``@route_with``

.. autofunction:: ferris.core.handler.route_with

For example::

    @route_with(template='/ultimate/life/form')
    def daleks(self):
        return 'Daleks'

Prefixes
--------

Prefixes must be explicitly listed in the ``prefix`` class property in a handler, for example::

    class Posts(Handler):
        prefixes = ['json']

        @route
        def json_stats(self):
            pass

        @route
        def xml_stats(self):
            pass

``json_stats`` will have the url ``/json/posts/stats`` but ``xml_stats`` will be at ``/posts/xml_stats``.


Generating URLs to Actions
--------------------------

There is a standard way to generate URLs to actions across the application:

.. automethod:: ferris.core.handler.Handler.uri(route_name = None, prefix = <sentinel>, handler = <sentinel>, action = <sentinel>, _pass_all = False, _full = False, *args, **kwargs)

Attempting to generate a URL to an action that doesn't exist will result in an exception.


Checking if an action exists
----------------------------

You can check for the existence of an action before attempting to generate a URL to it:

.. automethod:: ferris.core.handler.Handler.uri_exists

You can see if you're on a particular action. While this may seem like a superfluous feature, it's very useful in templates:

.. automethod:: ferris.core.handler.Handler.on_uri

Static Files
------------

Static files live in ``app/static`` and can be accessed via http://localhost:8080/static.

The folders ``css``, ``js``, and ``img`` are aliased and can be accessed via http://localhost:8080/css, http://localhost:8080/js, and http://localhost:8080/img respectively.

Plugin assets are available via http://localhost:8080/plugins/plugin_name/.
