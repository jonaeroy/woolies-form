Handlers
========

.. module:: ferris.core.handler

Handlers are responsible for processing and responding to HTTP requests. Handlers are typically lightweight classes that glue the :doc:`models` to the :doc:`templates`. Handlers can be extended with :doc:`components` and :doc:`scaffolded <scaffold>`.

Conventions
-----------

Handlers are named plural nouns in upper camel case (UpperCamelCase) from the models that they are associated with (for example: Pages, Users, Images, Bears, etc.). The are many cases where the plural convention doesn't make sense, such as handlers that don't have an associated model or handlers that span multiple models.

Each handler class should be in its own file under ``/app/handlers`` and the name of the file should be the underscored class name. For example, to create a handler to act on fuzzy bears, you would create the file ``/app/handlers/fuzzy_bears.py`` and inside of that define a class named ``FuzzyBears``.

Anatomy of a Handler
--------------------

.. autoclass:: ferris.core.handler.Handler

A handler is a class that inherits from :class:`~ferris.core.handler.Handler` and contains special methods called *actions*.

Actions are normal instance methods that can be invoked via HTTP. Ferris takes care of :doc:`automatically routing <routing>` actions and generating URLS.

This section mostly focuses on actions and how to process and respond to requests. Other features are tied into handlers in various ways. Handler actions are exposed via the :doc:`routing` system. Handlers can automatically discover and determine which :doc:`template <templating>` to use and render it. Handlers can process POST and JSON data and attach it to :doc:`forms`. Handlers also allow you to break out common functionality using :doc:`components`.


Requests
--------

Actions can access the current request using ``self.request``::

    def list(self):
        return self.request.path

For more information on the request object see the `webapp2 documentation on requests <http://webapp-improved.appspot.com/guide/request.html>`_.

Data
~~~~

Actions can also access the GET and POST variables using ``self.request.params``::

    def list(self):
        return self.request.params['text']

For just GET variables use ``self.request.GET``, and for POST only use ``self.request.POST``.

Parameters
~~~~~~~~~~~

Actions can also take various parameters on the URL as described in :doc:`routing`::

    def list(self, text, number):
        return text + str(number)

Context
~~~~~~~

Handler provides a bit of context about a request.

.. autoattribute:: Handler.action

.. autoattribute:: Handler.prefix

.. autoattribute:: Handler.user

.. autoattribute:: Handler.session

Response
--------

Actions can access the current response using ``self.response``::

    def list(self):
        self.response.write('hi')
        return self.response

For more information on the request object see the `webapp2 documentation on responses <http://webapp-improved.appspot.com/guide/response.html>`_.

Return Values
~~~~~~~~~~~~~

Actions can return a string and the string will become the body of the response::

    def list(self):
        return 'Hi!'

Actions can return an integer and the will become the status of the response, in this case the response will be a `404 Not Found`::

    def list(self):
        return 404

Actions can return any ``webapp2.Response`` class, including ``self.response``::

    def list(self):
        self.response.content_type = 'text/json'
        self.response.text = '[0,1,2]'
        return self.response

Even if you return a string or integer, any changes to ``self.response`` are kept (except for the body or status, respectively)::

    def list(self):
        self.response.content_type = 'text/html'
        return '<h1>Hello!</h1>'

Returning nothing (``None``) will trigger the automatic template rendering unless :attr:`~Handler.auto_render` is set to ``False``::

    def list(self):
        pass
        # Return nothing will cause /app/templates/handler/list.html to be loaded and rendered.

Redirection
~~~~~~~~~~~

Redirects can be generated using :meth:`redirect` and :meth:`~ferris.core.handler.Handler.uri`::
    
    @route
    def auto(self):
        return self.redirect(self.uri(action='exterminate', who='everything'))


Template Rendering
------------------

Handler contains a bit of logic to make rendering templates easier. By default, returning ``None`` from an action will trigger automatic template rendering. You can easily pass data from the handler to the template and control how the handler finds its template.

Data
~~~~

To provide data to the template use the :meth:`get` and :meth:`set` methods:

.. automethod:: Handler.set

.. automethod:: Handler.get

For example::

    def list(self):
        self.set(band="The Beatles")
        self.set({'members': ['John', 'Paul', 'George', 'Ringo']})
        self.get("band")  # Returns "The Beatles"

Determination
~~~~~~~~~~~~~

A Handler can automatically determine which template to use:

.. automethod:: Handler._get_template_name

If you're not serving up html, you can change the extension:

.. autoattribute:: Handler.template_ext

If you'd like to use a theme:

.. autoattribute:: Handler.theme

If you set ``template_name`` to the full path of the template that will be used instead of the result of :meth:`~Handler._get_template_name`. This allows you to use templates from other actions and even other handlers:

.. autoattribute:: Handler.template_name

For example::

    def list(self):
        self.template_name = 'shows/grid.html'


Rendering
~~~~~~~~~

By default, :attr:`auto_render` is enabled:

.. autoattribute:: Handler.auto_render

Of course, you can also manually render a template:

.. automethod:: Handler.render_template

For example::

    def list(self):
        return render_template('planets/earth.html')


JSON
----

Handler provides a built-in method for JSON encoding python objects:

.. automethod:: Handler.json

This can be used to respond to requests with JSON data easily::

    def numbers(self):
        return self.json(range(0,100))

.. note::
    You will have to set the ``content-type`` header to ``application/json`` manually. If many actions are responding with JSON, you can set this header in the :meth:`~Handler.startup` callback.


Keys
----

When passing ndb.Keys in parameters or URLs, use the following methods to encode & decode them:

.. automethod:: Handler.url_key_for

.. automethod:: Handler.key_from_string

For example::
    
    @route
    def one(self):
        item = Widget.find_by_name('screwdriver')
        return self.redirect(self.uri(action='two', id=self.url_key_for(item)))

    @route
    def two(self, id):
        item = self.key_from_string(id).get()
        return item.name


Callbacks and Events
--------------------

Handlers have various callbacks and events that are called during the lifecycle of a request. 

Events
~~~~~~

For a usual request, the order is:

#. template_vars
#. before_build_components, after_build_components
#. before_startup, startup(), after_startup
#. is_authorized
#. before_dispatch, after_dispatch
#. template_names (only if :meth:`~Handler._get_template_name` is called)
#. before_render, after_render (only if a template is rendered)
#. dispatch_complete

You can tap into these events using :attr:`Handler.events` which is a :class:`~ferris.core.event.NamedEvents` instance::

    def startup(self):
        self.events.before_dispatch += self.on_after_dispatch

The usual spot to register event listeners is in the :meth:`startup` callback (inside a handler) or during construction inside a component.

These events are broadcasted to the global event bus with the prefix ``handler_``.

Callbacks
~~~~~~~~~

To ease the use of these events while inside a handler, you can override the following callback methods:

.. automethod:: Handler.startup

.. automethod:: Handler.before_dispatch

.. automethod:: Handler.after_dispatch

.. automethod:: Handler.before_render

.. automethod:: Handler.after_render
