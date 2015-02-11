Templates
=========

Ferris uses the `Jinja2 <http://jinja.pocoo.org/>`_ template engine and adds a few helper functions and filters, some layouts, and a theme system.

Conventions
-----------

Templates are stored in `/app/templates/[handler]/[prefix_][action].html`. So if you had a handler named Bears and an action named picnic, you would create a file named ``/app/templates/bears/picnic.html``. If you have a handler named Pages and an action named view and the prefix is mobile, you would create the template at ``/app/template/pages/mobile_view.html``.

Concepts
--------

* *Templates* (or views) are used by :doc:handlers to display the result of actions.
* *Layouts* are used by templates to provide boilerplate code, templates inherit from layouts.
* *Elements* are small pieces of templates that are included to reduce code duplication.
* *Macros* are files that contain macros (reusable functions) and pieces of with more complex objects.
* *Themes* are a collection of templates, macros, layouts, and elements that can override those in the default theme.

Templates
---------

Usually, a template will inherit from a layout and provide one or more blocks with content::

    {% extends "layouts/default.html" %}

    {% block layout_content %}
        <div> Hello! </div>
    {% endblock %}

This is optional, a template can easily skip extending a layout and provide its own content::

    <div> This works too! </div>

Also, a template can inherit from any other valid template::

    {% extends "posts/list.html" %}

    {% block post_title %}
        <h1 class='super-large'>{{post.title}}</h1>
    {% endblock %}


Layouts
-------

Layouts reside inside of ``app/templates/layouts`` and serve as the base templates for regular templates to inherit from.

For example, here's a layout name ``large_text.html``::
    
    <h1>{% block content %}{% endblock %}</h1>

Here's a template that inherits from it::

    {% extends "layouts/large_text.html" %}

    {% block content %}Yeah, Big Text!{% endblock %}

For more info on template inheritence, see the `jinja2 docs on inheritance <http://jinja.pocoo.org/docs/templates/#template-inheritance>`_. 

Ferris provides two standard layouts

The Default Layout
~~~~~~~~~~~~~~~~~~

Located at ``layouts/default.html``, the default layout provides a simple Twitter Bootstrap layout and a few blocks.

.. describe:: layout_head_title

    Text inside of the ``<title>`` tag.

.. describe:: layout_head

    Markup inside of the ``<head>`` tag, useful for adding scripts and stylesheets.

.. describe:: layout_body

    Everything inside the body tag, wraps layout_content, layout_before_content, and layout_after_content

.. describe:: layout_content

    Content inside of the ``<div class='container'>`` tag, the common spot for overriding and placing content.

.. describe:: layout_before_content

    Content before the ``<div class='container'>`` tag

.. describe:: layout_after_content

    Content after the ``<div class='container'>`` tag

The Admin Layout
~~~~~~~~~~~~~~~~

Located at ``layouts/admin.html``, the admin layout is used by the :doc:scaffolding and provides a layout with a side bar and navigation bar.

It contains all of the same blocks as the default layout, plus:

.. describe:: layout_nav_bar
    
    Contains the top navigation bar.

.. describe:: layout_wrapper

    Contains layout_header, layout_sidebar, and layout_content

.. describe:: layout_header

    Contains the breadcrumb and sits between layout_nav_bar and the two columns.

.. describe:: layout_sidebar

    Contains the action pallete (or any other content to be placed in the sidebar).


Elements
--------

Elements are typically located in ``app/templates/elements`` or for very specific elements ``app/templates/[handler]/elements``. There's nothing special about element other than just the organization and the idea.

Take this element ``species.html`` for example::

    <div>
        <h1>{{species.name}}</h1>
        <h2>From {{species.planet}}</h2>
        <p>{{species.description}}</p>
    </div>

And this template that uses the element::

    {% for species in species_list %}
        {% include "elements/species.html" with context %}
    {% endfor %}

Built-in Elements
~~~~~~~~~~~~~~~~~

.. describe:: jquery-ui.html

    Includes the scripts and stylesheets needed for jquery ui.

.. describe:: debug/toolbook.html

    Includes the debug toolbox (click the small icon in the bottom-right corner).

.. describe:: admin/chosen.html

    Includes the chosen javascript library and inserts it on all select boxes on the page.

.. describe:: admin/fancybox.html

    Includes the fancybox javascript library.

.. describe:: admin/datepicker.html

    Includes the bootstrap datepicker javascript library.


Macros
------

Macros are usually located in ``app/templates/macros/[name].html``, although some things choose ``app/templates/[name]/macros.html``. Either way is valid. The first makes sense when macros are more general, whereas the second makes sense when macros are used only in one set of templates.

Macros are just files that contain a collection of `jinja2 macros <http://jinja.pocoo.org/docs/templates/#macros>`_. 


Themes
------

Themes are a collection of templates, elements, and macros that can override those in the root or default theme. Themes are located in ``app/templates/themes/[name]`` and their directory structure mirrors that of the root ``app/templates`` folder.

For example, if you have a root template structure like this::
    
    * posts
        * list.html
        * view.html
    * elements
        * post.html

And you created a new theme called ``mobile`` under ``app/templates/themes/mobile`` and created the following directory structure::

    * posts
        * view.html
    * elements
        * post.html

If you switch the theme to ``mobile``, then the template engine will use the ``posts/view.html`` and ``elements/post.html`` templates from the ``mobile`` folder, *however* because we did not specify a ``posts/list.html`` in the ``mobile`` theme, it will use the ``posts/list.html`` in the root theme. In short, if a theme doesn't have a template it will fallback and use the root theme's template.

You can set the theme using :attr:`Handler.theme <ferris.core.handler.Handler.theme>`.

Providing and Accessing Data
----------------------------

Data is provided via :meth:`~ferris.core.handler.Handler.set` and :meth:`~ferris.core.handler.Handler.get` in :class:`~ferris.core.handler.Handler`::

    self.set(species="Raxacoricofallapatorian")

This data can now be accessed by name in the template::

    This is a {{species}}!

Of course, more complex data can be provided such as a :class:`~ferris.core.ndb.Model` instance::

    self.set(species=Species.find_by_planet('Gallifrey'))

Properties on that object can be accessed in the template::

    The primary species of the planet {{species.planet}} is {{species.name}}.


Function, Filters, and Context
------------------------------

Ferris adds a few useful items to the template context.


Ferris Specific Utilities
~~~~~~~~~~~~~~~~~~~~~~~~~

.. function:: localize(datetime)
    :noindex:
    Maps to :func:`time_util.localize` to localize a datetime object.

.. function:: json(obj)
    :noindex:

    Uses :mod:`ferris.json_util` to serialize an object to JSON. Can also be used as a filter.

.. attribute:: inflector
    :noindex:

.. attribute:: ndb
    :noindex:

    Maps to ``google.appengine.ext.ndb``

The ``ferris`` object provides:

.. function:: ferris.is_current_user_admin()
    :noindex:

.. attribute:: ferris.users
    :noindex:

    Maps to ``google.appengine.api.users``

.. attribute::theme
    :noindex:

    The current theme

.. attribute::app_config
    :noindex:

    The ``app_config`` object from ``settings.py``

.. function::has_plugin(plugin)
    :noindex:

    Returns true if the given plugin is registered

The ``handler`` object provides:

.. attribute:: handler.name
    :noindex:

    The name of the current handler.

.. attribute:: handler.prefix
    :noindex:

.. attribute:: handler.action
    :noindex:

.. function:: handler.uri()
    :noindex:
    
    Maps to :meth:`ferris.core.Handler.uri` to generate urls.

.. function:: handler.uri_exists()
    :noindex:

.. function:: handler.on_uri()
    :noindex:

.. attribute:: handler.request
    :noindex:

.. function:: handler.url_key_for()
    :noindex:

.. function:: handler.user
    :noindex:

    The current user.


General Utilities
~~~~~~~~~~~~~~~~~

Most of these map 1:1 to their python equivalents.

.. function:: isinstance()
    :noindex:
.. function:: int()
    :noindex:
.. function:: float()
    :noindex:
.. function:: list()
    :noindex:
.. function:: str()
    :noindex:
.. function:: dir()
    :noindex:
.. attribute:: math
    :noindex:
.. attribute:: datetime
    :noindex:

