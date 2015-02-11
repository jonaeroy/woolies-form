import fix_imports

# Import the application
import settings
import ferris
import ferris.app
import ferris.routes
import app.routes
import app.listeners
from app import receiver

app = ferris.app.app  # the app object in the app package.

notification_receiver = receiver.app
# from google.appengine.ext.appstats import recording
# app = recording.appstats_wsgi_middleware(app)
