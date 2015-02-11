import wtforms.ext.appengine.db as wtfdb
import wtfndb
from . import fields


def reference_select_value(self):
    """
    Augment ReferenceProperty to have a _value function so it can be used with
    Hidden Input Widget
    """
    if self.data:
        return self.data.key()
    else:
        return '__None'

wtfdb.ReferencePropertyField._value = reference_select_value

# Monkey-patch wtf's converter for the SafeReferenceProperty
wtfdb.ModelConverter.default_converters['SafeReferenceProperty'] = (
    wtfdb.convert_ReferenceProperty)


### Additional Converters

# Monkey-patch wtf's converter for the User field
wtfdb.ModelConverter.default_converters['UserProperty'] = fields.convert_UserProperty
wtfndb.ModelConverter.default_converters['UserProperty'] = fields.convert_UserProperty
