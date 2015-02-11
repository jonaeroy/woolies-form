from ferris import Controller, messages, scaffold, route
from ..models.costcentre import Costcentre


class Costcentres(Controller):

    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, messages.Messaging)

    def add(self):
        return scaffold.add(self)

    def list(self):
        return scaffold.list(self)

    @route
    def save_import(self):
        number = int(self.request.get('Cost Centre'))
        store_name= self.request.get('Store Name')
        costcentre = Costcentre(number = number,
                    store_name=store_name)
        costcentre.put()

        result = True
        return self.util.stringify_json(result);