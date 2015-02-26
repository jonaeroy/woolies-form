from ferris.core import routing

from ferris.controllers.root import Root
from ferris.controllers.oauth import Oauth

routing.add(routing.Route('/admin', Root, handler_method='admin'))
routing.route_controller(Oauth)
