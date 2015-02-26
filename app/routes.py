from ferris.core import routing, plugins

# Routes all App handlers
routing.auto_route()

# Default root route
routing.redirect('/', to='/mains/dashboard')


# Plugins
plugins.enable('angular')
plugins.enable('tiny_mce')
plugins.enable('settings')
plugins.enable('oauth_manager')
plugins.enable('template_tester')
plugins.enable('service_account')
plugins.enable('directory')
plugins.enable('calendar')
plugins.enable('google_directory')
