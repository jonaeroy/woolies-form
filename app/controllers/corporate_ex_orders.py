from ferris import Controller, scaffold, route

class CorporateExOrders(Controller):

	class Meta:
		prefix = ('admin',)
		components = (scaffold.Scaffolding,)

	admin_list = scaffold.list

	@route
	def form_handler(self):
		pass