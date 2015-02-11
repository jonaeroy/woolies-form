Functional Testing
==================

We can add functional tests to our application to verify all of the functionality that we claim to have.
Ferris provides you with the ability to test our application's handlers in the same way that we tested
our data model.

Before we get started testing, we need to add a root route so that http://localhost:8080/ goes to
``/posts``.

Modify ``app/routes.py`` and remove these lines::

    from webapp2 import Route
    from ferris.handlers.root import Root
    ferris_app.router.add(Route('/', Root, handler_method='root'))

Add these lines in their place::

    from webapp2_extras.routes import RedirectRoute
    ferris_app.router.add(RedirectRoute('/', redirect_to='/posts'))

At this point opening http://localhost:8080/ should send us to http://localhost:8080/posts.

.. note::
    To run tests execute ``scripts/backend_test.sh`` or alternatively ``python ferris/scripts/test_runner.py app`` just as we did in the Data Model section.


The Sanity Test
---------------

Ferris provides an example test called ``SanityTest`` that resides in ``app/tests/backend/test_sanity.py``.

Here's the code for that test::

    class SanityTest(AppTestCase):

    def testRoot(self):
        self.loginUser()
        resp = self.testapp.get('/')

        self.loginUser(admin=True)
        resp = self.testapp.get('/admin')
        self.assertTrue('Ferris' in resp)

Let's walk through this:

* We create a test class by inheriting from ``AppTestCase``. ``AppTestCase`` handles loading and registering all of your handlers. It also gives you a test environment that is very similar to your full application.
* We start our test method by logging in a user. We can specify an email and whether or not the user is an admin, or we can use the default setup of test@example.com and no admin.
* Our test then makes a GET request to '/', our root url. If this fails to return a ``200`` response, our test will fail.
* Our test logs in an admin user.
* Now, we do a GET request to '/admin' and make sure that "Ferris" is somewhere in the body of the response.

We're going build on this example and create tests to verify:

* /posts is a list of all user's posts.
* /posts?mine is a list of only the logged-in user's posts.
* /posts contains edit links.
* /posts/add is a form and submitting that form will create a new item.
* /posts/edit doesn't allow users to edit posts that aren't theirs.

While this isn't an exhaustive list, it will demonstrate how to test various aspects of our application.


Testing Lists
-------------

In this test, we'll create four posts: two from the first user, and two from the second user.  We will then
check the results of our list methods. Our tests should verify that the data was created and appears as expected.


First, let's create our test class in ``app/tests/backend/test_posts.py``::

    from ferris.tests.lib import AppTestCase
    from app.models.post import Post


    class TestPosts(AppTestCase):

        def testLists(self):
            self.loginUser("user1@example.com")


We have a user logged in, so let's create some posts as that user::

    Post(title="Test Post 1").put()
    Post(title="Test Post 2").put()

Now let's log in the second user and create some more posts::

    self.loginUser("user2@example.com")

    Post(title="Test Post 3").put()
    Post(title="Test Post 4").put()

At this point we can now make requests and verify their content. Let's start with ``/posts`` and verify that all of the posts
are showing up::

    resp = self.testapp.get('/posts')

    assert 'Test Post 1' in resp.body
    assert 'Test Post 2' in resp.body
    assert 'Test Post 3' in resp.body
    assert 'Test Post 4' in resp.body

Very well, let's continue with ``/posts?mine`` and verify that only user2@example.com's posts are present::

    resp = self.testapp.get('/posts?mine')

    assert 'Test Post 1' not in resp.body
    assert 'Test Post 2' not in resp.body
    assert 'Test Post 3' in resp.body
    assert 'Test Post 4' in resp.body

Additionally, let's make sure the 'edit' links are present::

    assert 'Edit' in resp.body


Testing Add
-----------

Let's add a new method and make a request to ``/posts/add``::

    def testAdd(self):
        self.loginUser("user1@example.com")

        resp = self.testapp.get('/posts/add')

Now let's get the form from the response, try to submit it without filling it out, and verify that it caused a validation error::

    form = resp.form
    error_resp = form.submit()

    assert 'This field is required' in error_resp.body

With that in place, let's fill out the form, submit it, and verify that it went through::

    form['title'] = 'Test Post'
    good_resp = form.submit()

    assert good_resp.status_int == 302  # Success redirects us to list

Finally, load up the list and verify that the new post is there::

    final_resp = good_resp.follow()

    assert 'Test Post' in final_resp


Testing Edit
------------

To test to make sure that a user can only edit his own posts, we're going to need to create posts under
two different users like we did before::

    def testEdit(self):
        self.loginUser("user1@example.com")

        post_one = Post(title="Test Post 1")
        post_one.put()

        self.loginUser("user2@example.com")

        post_two = Post(title="Test Post 2")
        post_two.put()


Now, let's load the edit page for post two. This should succeed::

    self.testapp.get('/posts/:%s/edit' % post_two.key.urlsafe())

Finally, load the edit page for post one. We should expect this to fail::

    self.testapp.get('/posts/:%s/edit' % post_one.key.urlsafe(), status=401)


Next
----

Continue with :doc:`7_extras`
