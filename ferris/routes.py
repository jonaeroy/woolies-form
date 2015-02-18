from ferris.core import routing, plugins

routing.auto_route()

# from ferris.controllers.root import Root
# from ferris.controllers.oauth import Oauth

# routing.add(routing.Route('/admin', Root, handler_method='admin'))
# routing.route_controller(Oauth)


routing.redirect('/', to='ng-view')



plugins.enable('angular')
