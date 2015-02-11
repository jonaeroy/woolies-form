Scaffolding
===========

One of the most powerful and complex features of Ferris is scaffolding. Scaffolding provides *actions* and *templates* for the common CRUD actions: ``list``, ``add``, ``view``, ``edit``, and ``delete``.

Because scaffolding happens on both handlers and templates we will discuss those separately.


Handler Scaffolding
-------------------

The scaffold will provide your handler with the basic logic for the forementioned CRUD actions. You have to explicitly decorate the handler class and each action that you want scaffolded with the ``@scaffold`` decorator.

.. module:: ferris.core.scaffolding

.. autofunction:: scaffold

For example::

    from ferris.core.handler import Handler, scaffold

    @scaffold
    class Cats(Handler):

        @scaffold
        def list(self):
            pass

Anything inside of the function will be executed *after* the scaffold's behavior. You can use this to set your own template variables or interact with what the scaffold fetched for you::

    @scaffold
    def list(self):
        logging.info("There are %s cats" % self.get('cats').count())

You can invoke the scaffold method directly without decorating your action (the handler class must always be decorated). This allows you to execute code before the scaffold logic::

    @scaffold
    def view(self, id):
        if not self.user_can_view(id):
            return 401
        return self.scaffold.view(self, id)

Actions
~~~~~~~

The scaffold implements the CRUD actions as follows:

.. automethod:: ScaffoldHandler.list

.. automethod:: ScaffoldHandler.view

.. automethod:: ScaffoldHandler.add

.. automethod:: ScaffoldHandler.edit

.. automethod:: ScaffoldHandler.delete


Configuration
~~~~~~~~~~~~~

The scaffold can be configured in a few ways:

.. attribute:: ScaffoldHandler.Model

    The Model class that will be used for all scaffold actions. This can be automatically determined if your handler is named the plural form of your model (if you have a Cat model and a Cats handler, then self.Model will automatically be Cats). Of course, you can set it manually to use other models or switch the model for a particular action.

.. attribute:: ScaffoldHandler.ModelForm

    The Form class that will be used for the ``add`` and ``edit`` actions. If none is specified, it will be generated using :func:`ferris.core.forms.model_form`. You can set it manually to use different form for different actions, users, states, etc.

    Example::

        def public_add(self):
            self.ModelForm = PublicPostForm
            return self.scaffold.add(self)

    An instance of the modelform (with all form data processed) is accessabile via :meth:`ScaffoldHandler.get_modelform`.

.. attribute:: ScaffoldHandler.scaffold.display_properties

    A list of property names that will be shown for the ``list`` and ``view`` actions, this is useful when a Model has a ton of properties and only a few are really needed::

        @scaffold
        def list(self):
            self.scaffold.display_properties = ['name', 'created_by']

.. attribute:: ScaffoldHandler.scaffold.should_save

    If set to False, it will prevent ``add`` or ``edit`` from saving an item. This is useful for components that tap into the scaffolding behavior.

.. attribute:: ScaffoldHandler.scaffold.flash_messages

    Enables or disables flash messages. Flash messages are short messages that appear to the user on the next page. For example, when a user creates a new post, a success flash message is shown on the next page. It's often useful to disable this if you're doing things via ajax, as the flash message will never be cleared and may be shown on different page at a later time causing user confusion.

.. attribute:: ScaffoldHandler.scaffold.redirect

    By default, the scaffold will redirect the user to ``list`` whenever they successfully create or update using ``add`` or ``edit``. Setting this to False will disable the behavior.

.. attribute:: ScaffoldHandler.scaffold.form_action

    By default, the form tags ``action`` attribute is set to the current action in ``add`` and ``edit``. You can however override this and specify a different action for the form. This is used by the upload component.

Functions
~~~~~~~~~

.. method:: ScaffoldHandler.get_modelform(obj=None)

    Returns an instance of :attr:`ModelForm` that has been populated with the data from ``POST``, JSON, and the given object (if provided).

.. method:: ScaffoldHandler.flash(message, type='info')

    Sets the message to be flashed on the next page. Type can be 'info', 'warning', 'success', and 'error'.

Events
~~~~~~

Like :class:`~ferris.core.handler.Handler`, scaffold emits a events on the Handler that can be listened to by the Handler itself or any components.

#. scaffold_before_apply - happens before form data is applied to the model for ``add`` and ``edit``.
#. scaffold_before_save - happens before the model is ``put()`` to the datastore in ``add`` and ``edit``.
#. scaffold_after_save - happens after the model is ``put()`` to the datastore in ``add`` and ``edit``.
#. scaffold_before_delete - happens before the key is deleted in ``delete``.
#. scaffold_after_delete - happens after the key has been deleted in ``delete``.


EasyHandler
~~~~~~~~~~~

To keep you from having to specify all the CRUD actions to be scaffolded for admin/experimentation, you can use ``EasyHandler``:

.. autoclass:: ferris.core.easy_handler.EasyHandler


Template Scaffolding
--------------------

The scaffold provides templates for CRUD actions as well as utilities to help build templates.

Template Variables
~~~~~~~~~~~~~~~~~~

The following template variables are exposed by the scaffold:

.. describe:: scaffolding.name

    The name (underscored) of the current handler.

.. describe:: scaffolding.proper_name

    The class name of the current handler.

.. describe:: scaffolding.title

    The titleized version of the current handler's name.

.. describe:: scaffolding.pluralized

    The pluralized underscored version of the current handler's name.

.. describe:: scaffolding.singularized

    The singularizzed underscored version of the current handler's name.


CRUD Templates
~~~~~~~~~~~~~~

Scaffolding your handler class automatically allows any of the methods ``list``, ``view``, ``add``, ``edit``, and ``delete`` to use their respective scaffold templates. These templates are located in ``ferris/templates/scaffolding``. You can use these templates in two ways: falling back, or extending and overriding.

Falling back is easy: just don't create a template for your action. The scaffold will automatically use the scaffold template.

Extending and overriding involves creating a template for your action, but inheriting from the scaffold template and overriding blocks as needed. For example::

    {% extends "scaffolding/add.html" %}

    {% block submit_text %}
        Make it Happen!
    {% endblock %}


Macros
~~~~~~

The scaffold macros are located at ``ferris/templates/scaffolding/macros.html`` and can be imported using::

    {% import 'scaffolding/macros.html' as s with context %}

It's not suggested to import them as ``scaffolding`` as you'll overwrite the variables set by the handler. Use ``s`` or ``scaf``.

Scaffolding provides the following macros:

.. function:: s.admin_or_default()

    Returns the admin layout if the prefix is 'admin', otherwise returns the default layout. This is useful for using the same template for both admin and other prefixes.

    Example::

        {% extends s.admin_or_default %}

.. function:: s.print(value)

    Pretty prints a value. This is great for printing dates, list of items, etc.

.. function:: s.flash()

    Displays a flash message and clears the flash message queue.

.. function:: s.next_page_link()

    Generates the paginator (if the pagination component is present)
