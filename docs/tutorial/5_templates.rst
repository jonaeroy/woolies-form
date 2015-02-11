Templates
=========

At this point our application contains all of our essential functionality. However, it doesn't exactly
*look* like a blog. While the scaffolding templates are perfectly acceptable in some situations, there
are many situations where you'd like to create your own.


Layouts
-------

Most templates will use a layout. Layouts are stored in ``app/templates/layouts``. Ferris provides
two layouts for you: A simple `Twitter Bootstrap <http://twitter.github.com/bootstrap/>`_ (``default.html``) and a layout that's used for the
admin scaffold (``admin.html``).

.. note::
    If you're using the scaffold templates, Ferris will choose which one to use based on the prefix. Ferris uses ``admin.html`` for the ``admin`` prefix, and ``default.html`` for everything else.

You can override Ferris' ``default.html`` by creating your own. We're going to add some navigation at the top
of our application.

Create ``app/templates/layouts/default.html``::

    <!doctype html>
    <html>
    <head>
        <title>{{scaffolding.title}}</title>

        <link rel="stylesheet" type="text/css" href="/ferris/css/bootstrap.min.css">
        <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
        <script type="text/javascript" src="/ferris/js/bootstrap.min.js"></script>
    </head>
    <body>
        <div class="container">
            {% block layout_content %}
            {% endblock %}
        </div>
    </body>
    </html>

This is a very simple layout that more or less mimics what Ferris' ``default.html`` provides. The important
piece to note is the ``layout_content`` block. This creates a spot where child templates can insert content.


Navigation
----------

We're going to add the standard Bootstrap navbar to our layout with links to the list of all posts, the list
of the current user's posts, and the form to add a new post.

Add this inside of ``<div class="container">``::

    <div class="navbar">
        <div class="navbar-inner">
            <a class="brand" href="#">Blog</a>
            <ul class="nav">
                <li><a href="{{handler.uri('posts-list')}}">All</a></li>
                <li><a href="{{handler.uri('posts-list', mine=True)}}">Mine</a></li>
                <li><a href="{{handler.uri('posts-add')}}">New</a></li>
            </ul>
        </div>
    </div>

In this example we're using ``handler.uri`` to generate urls for particular actions.  ``handler.uri`` is a very powerful function
that generates an url to any action in your application.  When possible, use this method for generating urls; this method only generates urls
to valid actions and accepts custom urls created with ``@route_with``.

Notice that the first link (``<li><a href="{{handler.uri('posts-list')}}">All</a></li>``) generates a url to ``Posts.list`` using the canonical name ``posts-list``, while
the second link (``<li><a href="{{handler.uri('posts-list', mine=True)}}">Mine</a></li>``) adds the query parameter ``mine``. This also works with named parameters.

Canonical route names follow the simple convention ``prefix-handler-action``: ``TimeMachines.admin_list`` becomes ``admin-time_machines-list``.

If we open up http://localhost:8080/posts, we'll see that we have a nice top-level navigation bar.


Listing
-------

Presenting blog posts in a table isn't exactly the best way to it. We'd like to show the content of the post and
present everything in a way that's slightly easier on the eyes. At the moment we're using the scaffold's template
for ``list``, but we can easily use our own by creating ``app/templates/posts/list.html``::

    {% extends "layouts/default.html" %}
    {% import "scaffolding/macros.html" as scaffold with context %}

    {% block layout_content %}
        {% for post in posts %}
        <div class="media">
            <div class="media-body">
                <h4 class="media-heading">{{post.title}}</h4>
                <h6 class="media-heading">By {{post.created_by}} on {{scaffold.print(post.created)}}</h6>
                <p>{{post.content}}</p>
            </div>
        </div>
        {% endfor %}
    {% endblock %}

Let's walk through this one:

* First, we inherit from the default layout we created earlier.
* We also import the scaffold's macros. This provides us with a couple of useful helpers.
* We specify the content to put in the layouts ``layout_content`` block.
* We iterate over each post in the ``posts`` variable and create a media div for it.
* We use the ``scaffold.print`` method to output a nicely formatted and localized date.

Opening up http://localhost:8080/posts shows our much nicer list of posts.

It would be nice to have an edit link as well. Add this before the closing tag of ``<div class="media">``::

    {% if handler.user == post.created_by %}
        <a href="{{handler.uri('posts-edit', id=handler.url_id_for(post))}}">Edit</a>
    {% endif %}

Here we use the ``handler.url_id_for`` function to pass the proper id argument to ``Posts.edit``.

Now http://localhost:8080/posts shows an edit link for posts that the currently logged in user has created.


Next
----

Continue with :doc:`6_functional_testing`
