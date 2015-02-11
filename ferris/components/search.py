import logging
import datetime
from ferris.core import inflector
from google.appengine.api import search, users
from google.appengine.ext import ndb


class Search(object):
    """
    Provides a simple high-level interface to the App Engine Search API.
    """

    def __init__(self, controller):
        self.controller = controller

    def _get_index(self):
        if hasattr(self.controller.meta, 'search_index'):
            return self.controller.meta.search_index
        if hasattr(self.controller.meta, 'Model'):
            Model = self.controller.meta.Model
            if hasattr(Model.Meta, 'search_index'):
                return Model.Meta.search_index[0] if isinstance(Model.Meta.search_index, (list, tuple)) else Model.Meta.search_index
            return 'auto_ix_%s' % Model._get_kind()
        raise ValueError('No search index could be determined')

    def _get_limit(self):
        if hasattr(self.controller.meta, 'paginate_limit'):
            return self.controller.meta.paginate_limit
        return 100

    def _get_cursor(self):
        cursor = self.controller.request.params.get('cursor', None)
        return search.Cursor(web_safe_string=cursor) if cursor else search.Cursor()

    def search(self, index=None, query=None, limit=None, options=None):
        """
        Searches using the provided index (or an automatically determine one).

        Expects the search query to be in the ``query`` request parameter.

        Also takes care of setting pagination information if the :class:`pagination component <ferris.components.pagination.Pagnation>` is present.
        """

        index = index if index else self._get_index()
        limit = limit if limit else self._get_limit()
        query_string = query if query else self.controller.request.params.get('query', '')
        cursor = self._get_cursor()
        options = options if options else {}

        try:

            options_params = dict(
                limit=limit,
                ids_only=True,
                cursor=cursor)

            options_params.update(options)

            query = search.Query(query_string=query_string, options=search.QueryOptions(**options_params))
            index = search.Index(name=index)
            index_results = index.search(query)

            results = ndb.get_multi([ndb.Key(urlsafe=x.doc_id) for x in index_results])
            results = [x for x in results if x]

            self.controller.context.set_dotted('paging.limit', limit)
            self.controller.context.set_dotted('paging.cursor', cursor)
            self.controller.context.set_dotted('paging.count', len(results))
            if index_results.cursor:
                self.controller.context.set_dotted('paging.cursor', str(index_results.cursor.web_safe_string))

        except (search.Error, search.query_parser.QueryException) as e:
            results = []
            self.controller.context['search_error'] = e

        self.controller.context['search_query'] = query_string
        self.controller.context['search_results'] = results

        if hasattr(self.controller, 'scaffold'):
            self.controller.context[self.controller.scaffold.plural] = results

        return results

    __call__ = search


def convert_to_search_fields(data):
    results = []
    for key, val in data.iteritems():
        if isinstance(val, basestring):
            field = search.TextField(name=key, value=val)
        elif isinstance(val, datetime.datetime):
            field = search.DateField(name=key, value=val.date())
        elif isinstance(val, datetime.date):
            field = search.DateField(name=key, value=val)
        elif isinstance(val, users.User):
            field = search.TextField(name=key, value=unicode(val))
        elif isinstance(val, bool):
            val = 'true' if val else 'false'
            field = search.AtomField(name=key, value=val)
        elif isinstance(val, (float, int, long)):
            field = search.NumberField(name=key, value=val)
        else:
            field = None
            logging.info('Property %s couldn\'t be added because it\'s a %s' % (key, type(val)))
        if field:
            results.append(field)
    return results


def default_indexer(instance, properties):
    properties = [k for k in properties if
        (not isinstance(instance._properties[k], (ndb.BlobProperty, ndb.KeyProperty))
            or isinstance(instance._properties[k], (ndb.StringProperty, ndb.TextProperty)))]

    return {k: getattr(instance, k) for k in properties}


def index(instance, index, only=None, exclude=None, indexer=None, callback=None):
    """
    Adds an instance of a Model into full-text search.

    :param instance: an instance of ndb.Model
    :param list(string) only: If provided, will only index these fields
    :param list(string) exclude: If provided, will not index any of these fields
    :param callback: A function that will recieve (instance, fields), fields being a map of property names to search.xField instances.

    This is usually done in :meth:`Model.after_put <ferris.core.ndb.Model.after_put>`, for example::

        def after_put(self):
            index(self)

    """

    indexer = indexer if indexer else default_indexer
    indexes = index if isinstance(index, (list, tuple)) else [index]
    only = only if only else [k for k, v in instance._properties.iteritems() if hasattr(instance, k)]
    exclude = exclude if exclude else []
    properties = [x for x in only if x not in exclude]

    data = indexer(instance, properties)

    if callback:
        callback(instance=instance, data=data)

    fields = convert_to_search_fields(data)

    try:
        doc = search.Document(doc_id=str(instance.key.urlsafe()), fields=fields)
        for index_name in indexes:
            index = search.Index(name=index_name)
            index.put(doc)
    except Exception as e:
        logging.error("Adding model %s instance %s to the full-text index failed" % (instance.key.kind(), instance.key.id()))
        logging.error("Search API error: %s" % e)
        logging.error([(x.name, x.value) for x in fields])


def unindex(instance_or_key, index=None):
    """
    Removes a document from the full-text search.

    This is usually done in :meth:`Model.after_delete <ferris.core.ndb.Model.after_delete>`, for example::

        @classmethod
        def after_delete(cls, key):
            unindex(key)

    """
    if isinstance(instance_or_key, ndb.Model):
        instance_or_key = instance_or_key.key

    indexes = index if isinstance(index, (list, tuple)) else [index]

    for index_name in indexes:
        index = search.Index(name=index_name)
        index.delete(str(instance_or_key.urlsafe()))
