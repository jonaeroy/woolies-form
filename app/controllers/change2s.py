from ferris import Controller, scaffold, route

class Change2s(Controller):

	 class Meta:
	 	prefix = ('api',)
	 	components = (scaffold.Scaffolding,)

	 list = scaffold.list
	 delete = scaffold.delete
	 edit = scaffold.edit

	 @route
	 def costchangeform2(self):
	 	pass

