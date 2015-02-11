"""
Central place to store event listeners for your application,
automatically imported at run time.
"""
from ferris.core.events import on
from app.etc.auth import require_domain
from app.etc.auth import user_credentials
from app.etc.auth import is_manager_of_this_form
from app.etc.auth import set_approver_of_this_form


@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, require_domain)
    authorizations.insert(0, user_credentials)
    authorizations.insert(0, is_manager_of_this_form)
    authorizations.insert(0, set_approver_of_this_form)
