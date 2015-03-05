from ferris import Controller, messages, scaffold, route
from ..models.store import Store

class Stores(Controller):

    class Meta:
        prefixes = ('api', 'admin',)
        components = (scaffold.Scaffolding, messages.Messaging)
        Model = Store

    def add(self):
    	return scaffold.add(self)

    def list(self):
    	return scaffold.list(self)

    @route
    def api_list_all(self):
        self.context['data'] = Store.all_stores()

    @route
    def save_import(self):
        number = int(self.request.get('Store No'))
        name = self.request.get('Store Name')
        add1 = self.request.get('Address 1')
        add2 = self.request.get('Address 2')
        suburb = self.request.get('Suburb')
        state = self.request.get('State')
        postcode = self.request.get('Postcode')
        store = Store(number = number,
                    name = name,
                    address1 = add1,
                    address2 = add2,
                    suburb = suburb,
                    state = state,
                    postcode = postcode
                )
        store.put()

        result = True
        return self.util.stringify_json(result)
