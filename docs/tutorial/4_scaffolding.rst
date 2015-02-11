Scaffolding
===========

Now that we understand Handlers we're going to create one for Posts.

The Posts handler should have the following actions:

* List of all posts
* List of my posts
* View of a single post
* Form to add a new post
* Form to edit an existing post
* Action to delete an existing post

With what we've learned already you could write all of these actions yourself.
Fortunately, the bulk of this functionality is already provided to you by Ferris via
the Scaffold.

Admin Scaffolding & The EasyHandler
-----------------------------------

To demonstrate the full extent of what scaffolding can do, we're going to enable
Admin scaffolding for Posts using the ``EasyHandler`` class.

Create ``app/handlers/posts.py``::

    from ferris.core.easy_handler import EasyHandler, scaffold


    @scaffold
    class Posts(EasyHandler):
        pass


Open http://localhost:8080/admin/posts in your browser. You'll see that you have a complete
interface for managing posts.

Let's walk through what we did:

* We used ``EasyHandler`` instead of ``Handler``. ``EasyHandler`` adds the admin prefix and actions for us.
* We decorated our class with ``scaffold``. This enables us to use the scaffold's behavior.

There's a lot of magic going on here, but all ``EasyHandler`` does is save you the trouble of writing
this::

    @scaffold
    class Posts(Handler):
        prefixes = ['admin']

        @scaffold
        def admin_list(self):
            pass

        @scaffold
        def admin_view(self, id):
            pass
        ...

Let's walk through what ``EasyHandler`` does for us:

* Sets ``prefixes`` to ``['admin']``. Prefix Routing allows you to have actions that live under a common prefix. For example, ``Posts.admin_custom`` becomes ``/admin/posts/custom``. If you add the prefix 'deadly' along with an action 'xml', the url ``deadly/posts/xml`` will display the results of taking that action.
* Adds the actions ``list``, ``view``, ``admin_list``, ``admin_add``, ``admin_view``, ``admin_edit``, and ``admin_delete`` decorated with ``scaffold`` in order to use the scaffold's functionality. Those actions (even when prefixed) are automatically routed.


Exploring the Scaffold
----------------------

Let's take a moment to explore the features that the admin scaffold provides us. Open http://localhost:8080/admin/posts
again and click 'Add' on the left navigation.

Here we see that a form has been automatically generated for the two fields in our Post model. Recall that we made the
title property required. If we try to submit this form without putting anything in the title field, we'll see that we
get a nicely formatted error field.

Let's go ahead and create an actual post with a title and content.  Once we've submitted the form, we'll be redirected to the list. Our new post has appeared.

On the right side of our new Post there are three buttons: view, edit, and delete. These map to the actions ``admin_view``, ``admin_edit``, and ``admin_delete``.


Listing Posts
-------------

Our requirements state that we need to have two different lists: one of everyone's posts, and one of just our posts.
This means that we need to build on top of the scaffold's list action to conditionally add a filter.

First, create a few posts as one user and a few posts as another user using the Admin scaffold so that we have some
data to test with.

.. note::
    You can sign in as a different user via the url http://localhost:8080/_ah/login. You'll want keep being an admin
    so you can add posts via the Admin scaffold.

If we open http://localhost:8080/posts we'll see that ``EasyHandler`` has provided us with a scaffolded ``list``
action that lists everyone's posts. However, they're in the wrong order. We need to modify it to
use the ``all_posts`` method from our Posts class.

First, let's pull ``EasyHandler``'s scaffolded ``list`` action into our class so we can modify it. Add this to our Posts handler::

    @scaffold
    def list(self):
        pass

This produces the same functionality that ``EasyHandler`` gives us by default. We need to do a couple of things to use our
``all_posts`` methods. First, we need to remove the ``scaffold`` decorator from the action to remove the scaffold behavior. Second, we need to call our method and set the ``posts`` template variable.

Modify our ``list`` action to this::

    def list(self):
        self.set(posts=self.Model.all_posts())

Notice that we're still able to use the scaffold's template; all we had to do was set the ``posts`` template variable
and the scaffold knew what to display. You'll also notice that the scaffold automatically determined that the ``Posts``
controller uses the ``Post`` model and provides that via ``self.Model``.

With that in place all that's left is to add the ability for list to show just our posts using the ``all_posts_by_user``
method. Modify the ``list`` method::

    def list(self):
        if 'mine' in self.request.params:
            self.set(posts=self.Model.all_posts_by_user())
        else:
            self.set(posts=self.Model.all_posts())

Now if we open up http://localhost:8080/posts?mine it will show only the posts for the currently logged-in user.


Adding Posts
------------

As nice as the admin scaffold is, we don't want to have to give every user admin rights to be able to add a new
post. We can give all users that ability by adding a non-prefixed ``add`` action::

    @scaffold
    def add(self):
        pass

We'll just use the scaffold's behavior since it is perfectly acceptable for this case. If we open up http://localhost:8080/posts/add we'll see a form like the one in the admin scaffolding.


Editing Posts
-------------

At this point users can add posts but they can't edit any of the posts they've already created. Let's
add the ``edit`` using the scaffold like we did with ``add``::

    @scaffold
    def edit(self, id):
        pass

Notice that we needed to add the second parameter ``id`` to this action. ``id`` is needed for ``view``, ``edit``, and ``delete`` in order to determine the correct item to edit.

At this point we have a problem: a user can edit *any* post, even those created by other users. While this could be slightly
amusing, this behavior is undesirable. We need to add a check to make sure the user is editing a post that they created::

    def edit(self, id):
        post = self.key_from_string(id).get()

        if post.created_by != self.user:
            return 401

        return self.scaffold.edit(self, id)

Let's walk through this:

* First, we need to get the post that the user is trying to edit. We need an ``ndb.Key`` in order to get the Post entity, and :meth:`~ferris.core.handler.Handler.key_from_string` does that for us.
* Second, we need to make sure the post was created by the same user that's logged in. :attr:`~ferris.core.handler.Handler.user` is always set to the currently logged in user.
* Returning ``401`` automatically creates a 401 Unauthorized response.
* If everything went well, we want to use the scaffold's behavior. Even if we remove the ``scaffold`` decorator from an action, we can still call the scaffold's version of the action using ``self.scaffold``.

Now users may not edit posts that they did not create.  However, they are still allowed to edit one of their own posts without a problem.


Next
----

Continue with :doc:`5_templates`
