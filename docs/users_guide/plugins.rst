Plugins
=======

Plugins are a simple way of re-using code across projects. Plugins consist of models, handlers, views, templates, and other python modules that exist together in a folder. Plugins mostly match 1-to-1 the organizational structure of the ``app`` directory, with a few caveats.

Creating A Plugin
-----------------

To create a plugin:

* Create a folder in ``plugins`` named after you plugin, like ``plugins/test``.
* Create a ``__init__.py`` file in your plugin like so::

    from ferris.core.plugins import register_plugin

    register_plugin('test')

* Create your models, handlers, templates in the plugins directory just as you would with ``app``.


Enabling Plugins
----------------

Before a plugin can be used, you must enable it in ``app/routes.py`` like so::

    enable_plugin('test')


Using Plugins
-------------

When a plugin is enabled, all of its handlers are routed just as if they existed in ``app``. This will cause collisions if you're using plugins that share handler names.

Similarly, all of a plugins templates can be accessed just as if they existed in ``app/templates``, though it is important to note that templates in ``app/templates`` have precendence over plugin templates to allow an app to override a plugin's template.

You can use any module in your plugin by importing it, for example::

    from plugins.cats.models.cat import Cat

Plugin Assets
-------------

Plugin assets are stored in the ``static`` directory inside of the plugin and are available via http://localhost:8080/plugins/plugin_name/
