Modeling Data
=============

First and foremost we need a way to store our data. Ferris uses the native Google App Engine
Datastore and the `ndb module <https://developers.google.com/appengine/docs/python/ndb/>`_. This section will walk you through creating a Model and how to
interact with it.

Models reside inside of `app/models`, let's create our Post model at `app/models/post.py`::

    from ferris.core.ndb import BasicModel
    from google.appengine.ext import ndb


    class Post(BasicModel):
        title = ndb.StringProperty()
        content = ndb.TextProperty()

This is a very simple model with only two fields: the title of the post, and the post's content. You may say, "wait, we also need to know who created that post and when!" You would be right, which is why we used ``BasicModel``. BasicModel extends from ``ferris.core.ndb.Model`` and provides us with four automatic fields::

    created = ndb.DateTimeProperty(auto_now_add=True)
    created_by = ndb.UserProperty(auto_current_user_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    modified_by = ndb.UserProperty(auto_current_user=True)

Since these fields are often necessary they're provided as part of the core framework.

.. note::
    Models are by convention singular nouns.

Experimenting with your model
-----------------------------

At this point we have a model, so let's get a feel for how to interact with it.

The App Engine Development Server has an excellent feature: the Interactive Console. Open http://localhost:8080/_ah/admin in your browser and click on 'Interactive Console' in the sidebar.

Enter this into the Interactive Console::

    from app.models.post import Post

    # Create a new post
    post = Post(title="Test Post", content="A basic post")

    # Save the post, it doesn't exist in the datastore until put() is called
    post.put()

    print post.title
    print post.content

    # Modify the title, and save it again.
    post.title = "A new title"
    post.put()

    # Get a fresh copy
    post2 = post.key.get()

    print post.title

    # Delete the post, we no longer need it.
    post.key.delete()


This snippet walks you through the basics of interacting with a model: creating, reading, updating, and deleting.

.. note::
    Most of the examples below should be entered into the interactive console unless otherwise stated.


Required fields
---------------

Often it's desirable to make sure a field is present before allowing an entity to be saved. This is quite easy.

Let's modify our Post class::

    class Post(BasicModel):
        title = ndb.StringProperty(required=True)
        content = ndb.TextProperty()

Let's create a post without a title::

    from app.models.post import Post

    post = Post(content="A basic post")

    # Raises a BadValueError
    post.put()

Ferris will recognize required fields when building forms.  If a required field is omitted, the end user will see a nicely formatted validation error.


Querying
--------

Ferris models are ``google.appengine.ext.ndb.Model`` subclasses, so you can use any and all methods of `querying <https://developers.google.com/appengine/docs/python/ndb/queries>`_ ordinary models.

However, Ferris does provide you with some shortcuts::

    from app.models.post import Post
    from google.appengine.api import users

    # create some posts
    Post(title="Post One", content="...").put()
    Post(title="Post Two", content="...").put()

    # Find just that first post.
    print Post.find_by_title("Post One").title

    # Find all posts by the current user.
    print list(Post.find_all_by_created_by(users.get_current_user()))

Our requirements call for the following queries on Posts:

* All posts in descending date order.
* Posts from a given user in descending date order.


Create these queries as methods on the Posts class.  Any and all consumers of Posts will use the queries defined in the class method, making it easy to adjust the query for all consumers.  This is the "fat model" approach.

Here's our modified Post model with these query methods::

    from ferris.core.ndb import BasicModel
    from google.appengine.ext import ndb
    from google.appengine.api import users


    class Post(BasicModel):
        title = ndb.StringProperty(required=True)
        content = ndb.TextProperty()

        @classmethod
        def all_posts(cls):
            """
            Queries all posts in the system, regardless of user, ordered by date created descending.
            """
            return cls.query().order(-cls.created)

        @classmethod
        def all_posts_by_user(cls, user=None):
            """
            Queries all posts in the system for a particular user, ordered by date created desceding.
            If no user is provided, it returns the posts for the current user.
            """
            if not user:
                user = users.get_current_user()
            return cls.find_all_by_created_by(user).order(-cls.created)

Now you can use ``Post.all_posts()`` and ``Post.all_posts_by_user()`` to execute these queries.


Testing your model
------------------

All of the tests for your application reside inside of `app/tests/backend`. We're going to create a
test to ensure that our model's query methods do exactly as we expect.

Create the following file in `app/tests/backend/test_post.py`::

    from ferris.tests.lib import WithTestBed
    from app.models.post import Post


    class TestPost(WithTestBed):

        def testQueries(self):
            # log in user one
            self.loginUser('user1@example.com')

            # create two posts
            post1 = Post(title="Post 1")
            post1.put()
            post2 = Post(title="Post 2")
            post2.put()

            # log in user two
            self.loginUser('user2@example.com')

            # create two more posts
            post3 = Post(title="Post 3")
            post3.put()
            post4 = Post(title="Post 4")
            post4.put()

            # Get all posts
            all_posts = list(Post.all_posts())

            # Make sure there are 4 posts in total
            assert len(all_posts) == 4

            # Make sure they're in the right order
            assert all_posts == [post4, post3, post2, post1]

            # Make sure we only get two for user2, and that they're the right posts
            user2_posts = list(Post.all_posts_by_user())

            assert len(user2_posts) == 2
            assert user2_posts == [post4, post3]

This test is lengthy but it adequately covers the functionality we require from our data model.

We can continue with the confidence that our data model and its queries are sound. To run these tests,
execute ``scripts/backend_test.sh`` or alternatively ``python ferris/scripts/test_runner.py app``.

.. note::
    Windows users or users with a non-standard install will have to provide the ``-sdk`` argument to the test runner with the path to your Google App Engine SDK.

Your output should resemble this::

    testQueries (app.tests.backend.test_post.TestPost) ... ok
    testRoot (app.tests.backend.test_sanity.SanityTest) ... ok
    testRoot (app.tests.test_sanity.SanityTest) ... ok

    ----------------------------------------------------------------------
    Ran 3 tests in 0.298s

    OK


Next
----

Continue with :doc:`3_handlers`
