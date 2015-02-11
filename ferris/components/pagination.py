from ferris.core import inflector
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
import logging


class Pagination(object):
    """
    Provides automatic pagination of ``db.Query`` and ``ndb.Query`` objects.

    Automatically happens for any ``list`` actions but can also be manually invoked
    via :meth:`paginate`.

    In automatic operation, it looks for a template variable with the underscored pluralized version of the Handler's name. For instance, if you're on ``Pages`` it looks for the template variable ``pages``.
    """

    def __init__(self, controller):
        self.controller = controller

        if not hasattr(self.controller.components, 'SplitView'):
            self.auto_paginate = False
        else:
            self.auto_paginate = True

        if not hasattr(self.controller.meta, 'pagination_action'):
            setattr(self.controller.meta, 'pagination_actions', ('list',))
        self.controller.events.after_dispatch += self.after_dispatch_callback.__get__(self)

    def _get_query(self, name):
        if not name and hasattr(self.controller, 'scaffold'):
            name = self.controller.scaffold.plural

        if isinstance(name, basestring):
            query = self.controller.context.get(name, None)
        else:
            query = name

        if not isinstance(query, (ndb.Query,)):
            logging.info('Unable to paginate, couldn\'t locate a query')
            return None

        return query

    def paginate(self, query=None, cursor=None, limit=None):
        """
        Paginates a query and sets up the appropriate template variables.

        Uses ``handler.paginate_limit`` to determine how many items per page, or defaults to 10 if omitted.

        Sets the ``paging`` template variable to a dictionary like::

            {
                "cursor": "abc...",
                "next_cursor": "nzb...",
                "limit": 10
            }

        Returns the data, and if ``query_or_var_name`` is a string, sets that template variable.
        """
        if self.auto_paginate == True:

            cursor = cursor if cursor else self.controller.request.params.get('cursor', None)
            if cursor and not isinstance(cursor, Cursor):
                cursor = Cursor(urlsafe=cursor)

            limit = limit if limit else self.controller.meta.pagination_limit if hasattr(self.controller.meta, 'pagination_limit') else 100
            query = self._get_query(query)

            if not query:
                return

            data, next_cursor, more = query.fetch_page(limit, start_cursor=cursor)

            if hasattr(self.controller, 'scaffold'):
                self.controller.context[self.controller.scaffold.plural] = data

            self.controller.context.set_dotted('paging.cursor', cursor.urlsafe() if cursor else False)
            self.controller.context.set_dotted('paging.next_cursor', next_cursor.urlsafe() if more else False)
            self.controller.context.set_dotted('paging.limit', limit)
            self.controller.context.set_dotted('paging.count', len(data))

            #Paging Tweak
            self.controller.context.set_dotted('paging.current', query.count())
            self.controller.context.set_dotted('paging.total', (query.count()/limit) + 1)
            self.controller.context.set_dotted('paging.query_count', query.count())

            return data, next_cursor if more else False
        else:
            return

    def after_dispatch_callback(self, response, *args, **kwargs):
        if self.controller.route.action in self.controller.meta.pagination_actions:  # checks for list and any prefixed lists
            self.paginate()
