from ferris.core.ndb import Behavior
from ferris.components import search


default_indexer = search.default_indexer


class Searchable(Behavior):
    def _get_index(self):
        if hasattr(self.Model.Meta, 'search_index'):
            return self.Model.Meta.search_index
        else:
            return 'auto_ix_%s' % self.Model._get_kind()

    def after_put(self, instance):
        only = self.Model.Meta.search_fields if hasattr(self.Model.Meta, 'search_fields') else None
        exclude = self.Model.Meta.search_exclude if hasattr(self.Model.Meta, 'search_exclude') else None
        indexer = self.Model.Meta.search_indexer if hasattr(self.Model.Meta, 'search_indexer') else None
        callback = self.Model.Meta.search_callback if hasattr(self.Model.Meta, 'search_callback') else None
        search.index(
            instance=instance,
            index=self._get_index(),
            only=only,
            exclude=exclude,
            indexer=indexer,
            callback=callback)

    def before_delete(self, key):
        search.unindex(key, self._get_index())
