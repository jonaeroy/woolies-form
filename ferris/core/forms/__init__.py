import wtforms_json
wtforms_json.init()
from google.appengine.ext import db, ndb
import wtforms.ext.appengine.db as wtfdb
import wtfndb
import fields
import widgets
import monkey

__all__ = ['model_form', 'fields', 'widgets']


def model_form(model, *args, **kwargs):
    """
    Generates a Form class automatically from a Model class.
    For more information an the full list of arguments, see the `wtforms documentation <http://wtforms.simplecodes.com/docs/1.0.2/ext.html#module-wtforms.ext.appengine>`_.
    """
    if issubclass(model, db.Model):
        return wtfdb.model_form(model, *args, **kwargs)
    elif issubclass(model, ndb.Model):
        return wtfndb.model_form(model, *args, **kwargs)
