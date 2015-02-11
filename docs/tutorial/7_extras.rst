Extras
======

At this point our application is complete and tested. At this point you can dive right in to the User's Guide, but there are a few extra things we can add to further demonstrate some more of Ferris' capabilities.


Pagination
----------

Ferris uses *Components* as a way of organizing commonly used functionality for Handlers. Ferris comes with a handful of built-in components and includes one for automatic pagination for list methods.

It's pretty easy to use. First import it::

    from ferris.components.pagination import Pagination

Then add it to our handler's component list and set the limit::

    @scaffold
    class Posts(EasyHandler):
        components = [Pagination]
        paginate_limit = 5

If you open up http://localhost:8080/posts, you'll see that it will show no more than five posts. However, we don't currently
have a way to move between pages. Luckily, the scaffolding macros can handle that.

Add this to our ``list.html`` template right before the end of the ``layout_content`` block::

    {{scaffold.next_page_link()}}

Now there is a paginator at the bottom of the page.


Searching
---------

Another useful component is search. It is slightly more difficult to use but still quite easy.

First, we need to modify our model.

Import the index and unindex functions::

    from ferris.components.search import index, unindex

Add two methods::

    def after_put(self, key):
        index(self)

    @classmethod
    def after_delete(cls, key):
        unindex(key)

These are model callbacks (covered more extensively in the User's Guide) that will index and unindex a post whenever it is saved or deleted.

.. note::
    Any posts created before you made this change will not be searchable until you edit and resave them.

Import the ``Search`` component and add it to our ``Posts`` handler::

    from ferris.core.easy_handler import EasyHandler, scaffold, route
    from ferris.components.pagination import Pagination
    from ferris.components.search import Search


    @scaffold
    class Posts(EasyHandler):
        components = [Pagination, Search]

Now let's add a new ``search`` action::

    def search(self):
        self.components.search.search()

Import the search macros into ``templates/posts/list.html``::

    {% import 'macros/search.html' as search with context %}

Finally, add these somewhere at the top of the inside of the ``layout_content`` block::

    {{search.search_filter(action='list')}}
    {{search.search_info()}}

Now when we visit http://localhost:8080/posts there should be a search box from which we can search through all posts.

