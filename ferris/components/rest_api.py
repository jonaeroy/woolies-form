from google.appengine.ext import db, ndb
from ferris.core import inflector
import logging


class RestApi(object):
    """
    Hooks into rendering to automatically provide a nice rest API
    """

    def __init__(self, handler):
        self.handler = handler
        self.view = None
        self.paginate = True
        self.prefixes = ['api']

        self.handler.events.before_dispatch += self.before_dispatch_callback.__get__(self)
        self.handler.events.after_dispatch += self.after_dispatch_callback.__get__(self)

    def before_dispatch_callback(self, *args, **kwargs):
        if self.handler.prefix in self.prefixes:
            if not self.view:
                if self.handler.action in ['list', 'search']:
                    self.view = 'list'
                elif self.handler.action in ['add', 'edit']:
                    self.view = 'form'
                elif self.handler.action in ['view', 'delete']:
                    self.view = 'single'
        if self.view:
            self.handler.components.json.render_as_json = True
            if hasattr(self.handler, 'scaffold'):
                self.handler.scaffold.redirect = False

    def after_dispatch_callback(self, response, *args, **kwargs):
        if not response and self.handler.prefix in self.prefixes and self.view:
            if self.view == 'form':
                self.process_form()
            elif self.view == 'single':
                self.process_single()
            elif self.view == 'list':
                self.process_list()
            self.handler.components.json.render_as_json = True
            self.handler.components.json.render()

    def process_single(self):
        pass

    def process_list(self):
        data = {}

        if self.paginate:
            paging = self.handler.get('paging')

            if not paging and 'pagination' in self.handler.components:
                self.handler.components.pagination.paginate()
                paging = self.handler.get('paging')

            if paging:
                data.update({
                    'itemsPerPage': paging['limit'],
                    'cursor': paging['cursor'],
                    'nextCursor': paging['next_cursor'] if paging['next_cursor'] else None,
                    'nextLink': self.handler.uri(
                        cursor=paging['next_cursor'], _pass_all=True, _full=True)
                        if paging['next_cursor'] else None,
                })

        items = self.handler.get(
            inflector.pluralize(self.handler.name),
            self.handler.get('data', None))

        if isinstance(items, (db.Query, ndb.Query)):
            item_count = items.count()
        else:
            item_count = len(items)

        data.update({
            'itemCount': item_count,
            'selfLink': self.handler.uri(_pass_all=True, _full=True),
            'items': items
        })

        self.handler.set(data=data)

    def process_form(self, form=None):
        if hasattr(self.handler, 'modelform'):
            if not form:
                form = self.handler.modelform
            if form.errors:
                self.handler.response.set_status(400)
                self.handler.set(data={'errors': form.errors})
            else:
                if self.handler.get('added_item'):
                    self.handler.response.set_status(201)
