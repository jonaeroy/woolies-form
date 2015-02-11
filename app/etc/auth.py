import os, logging
from google.appengine.api import users
from ..models.user import User
from ..models.woolies_form import WooliesForm
from ..models.group import Group
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import json


def require_domain(controller):
    if not controller.user:
        return False, "You must be logged in"

    #user = 'ray@cloudsherpas.com'
    user = users.get_current_user().email()
    domain = user.split('@').pop()

    #logging.info("USER =====>" + str(user))

    # Test domains
    if app_identity.get_application_id() =='woolworths-forms' and domain not in (
        'cloudsherpas.com',
        'bigw.com.au',
        'bws.com.au',
        'countdown.co.nz',
        'danmurphys.com.au',
        'masters.com.au',
        'progressive.co.nz',
        'siw.com.au',
        'thomasdux.com.au',
        'woolworths.com.au',
        'wowliquor.com.au',
        'firstestate.com.au',
        'woolworths.com.au',
        'woolworthskproc.com.au',
        'pinnacleliquor.com.au',
        'thewinequarter.com.au',
        'pinnacledrinks.com.au',
        'woolworthspetrol.com.au'
        ):
        return False, "Your domain does not have access to this application"

    return True


def user_credentials(controller):
    import os
    PRODUCTION_MODE = not os.environ.get(
        'SERVER_SOFTWARE', 'Development').startswith('Development')
    if not PRODUCTION_MODE:
        from google.appengine.tools.devappserver2.python import sandbox
        sandbox._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']

    if not controller.__class__.__name__ == "Googlecalendaremails":
        if not controller.session.get('user'):

            query = User.query(User.email == users.get_current_user().email())
            woolies_users = query.fetch(1)

            if bool(len(woolies_users)):
                user = woolies_users[0]
                #logging.info(user)
            else:
                user = None

            if user:
                user_isAdmin = user.role == 'Administrator' and True or False
                user_group = user.group
                user_fullname = user.fullname
                favorites = json.loads(user.favorites)
            else:
                user_isAdmin = False
                user_group = None
                user_fullname = None
                favorites = []

            user_isGoogleAdmin = users.is_current_user_admin() and True or False
            if user_isAdmin or user_isGoogleAdmin:
                user_isAdmin = True
            else:
                user_isAdmin = False

            try:
                
                _set = user.banner_category.get()
                user_banner_category = _set.name
            except:
                user_banner_category = None

            #logging.info("admin? " + str(user_isAdmin))
            wf = WooliesForm.all()
            wf.order(WooliesForm.name)
            wfresults = wf.fetch()

            controller.session['user_isAdmin'] = user_isAdmin
            controller.session['user_isGoogleAdmin'] = user_isGoogleAdmin
            controller.session['user_group'] = user_group
            controller.session['user_fullname'] = user_fullname
            controller.session['user_email'] = str(users.get_current_user().email()).lower()
            controller.session['logout'] = users.create_logout_url(controller.request.uri)
            controller.session['woolies_forms'] = wfresults
            controller.session['DOMAIN_PATH'] = str(app_identity.get_default_version_hostname())
            controller.session['APP_ID'] = str(app_identity.get_application_id())
            controller.session['group_list'] = Group.all()
            controller.session['user_favorites'] = favorites
            controller.session['user_banner_category'] = user_banner_category

            controller.context['route'] = controller.route.action

            for key, value in controller.session.items():
                controller.context[key] = value

    return True


def is_manager_of_this_form(controller):

    # get key based on main controller name
    PATH = controller.name
    CONTROLLER_KEY = None
    isFormAdmin = False
    formAdmin = None
    form = None
    isUserManagerOfForm =  False
    string_key = None

    try:        
        CONTROLLER_KEY = controller.request.params['key']
        controller.session[PATH + "_KEY"] = CONTROLLER_KEY
    except:
        try:
            CONTROLLER_KEY = controller.session[PATH + "_KEY"]
        except KeyError:
            CONTROLLER_KEY = None
            controller.session[PATH + "_KEY"] = CONTROLLER_KEY
            pass
    
    if CONTROLLER_KEY is not None:

        string_key = CONTROLLER_KEY
        form_key = ndb.Key(urlsafe=string_key)
        form = form_key.get()
        user_group = controller.session.get('user_group')
        try:
            formAdmin = form.form_administrator
        except:
            formAdmin = None
        isUserManagerOfForm = False

        if user_group:
            # check if first level approver
            for group in user_group:
                try:
                    if form.first_level_manager == group:
                        isUserManagerOfForm = True
                        break
                except Exception:
                    isUserManagerOfForm = False

            # check if second level approver
            for group in user_group:
                try:
                    if form.second_level_manager == group:
                        isUserManagerOfForm = True
                        break
                except Exception:
                    isUserManagerOfForm = False
            
        # check if form administrator
        if form and user_group:
            for group in user_group:
                try:          
                    if form.form_administrator == group:
                        isFormAdmin = True
                        break
                except:
                    isFormAdmin = False 

        #show also all list if FORM admin
        if  isFormAdmin == True:
            isUserManagerOfForm = True

        #show also all list if admin
        if controller.session.get('user_isAdmin') == True:
            isUserManagerOfForm = True
        
    controller.context['user_isManager'] = isUserManagerOfForm  # boolean (if going to show all the list)
    controller.context['form_key'] = string_key                 # form key as String
    controller.context['form_entity'] = form                    # form entity
    controller.context['form_admin'] = formAdmin                # Group Key object 
    controller.context['user_isFormAdmin'] = isFormAdmin        # boolean

    return True


def set_approver_of_this_form(controller):
    # get key based on main controller name
    PATH = controller.name
    try:
        CONTROLLER_KEY = controller.request.params['key']
        controller.session[PATH + "_KEY"] = CONTROLLER_KEY 
    except:
        try:
            CONTROLLER_KEY = controller.session[PATH + "_KEY"]
        except KeyError:
            CONTROLLER_KEY = None
            controller.session[PATH + "_KEY"] = CONTROLLER_KEY
            pass
    
    if CONTROLLER_KEY is not None:
        form_key = ndb.Key(urlsafe=CONTROLLER_KEY)
        form = form_key.get()

        group1 = None
        group2 = None
        
        try:
            group1 = form.first_level_manager.get()            
        except Exception:            
            group1 = None

        try:
            group2 = form.second_level_manager.get()
        except Exception:
            group2 = None

        user_group = controller.session.get('user_group')

        # set the the approver, give the entity
        controller.context['first_group_approver'] = group1
        controller.context['second_group_approver'] = group2

        #check if the user is part of the approvers
        is_first_group_approver = False
        is_second_group_approver = False

        if user_group:
            for group in user_group:
                try:
                    if group == group1.key:
                        is_first_group_approver = True
                        break
                    else:
                        is_first_group_approver = False
                    
                except:
                    is_first_group_approver = False

            for group in user_group:
                try:
                    if group == group2.key:
                        is_second_group_approver = True
                        break
                    else:
                        is_second_group_approver = False
                except:
                    is_second_group_approver = False

        controller.context['is_first_group_approver'] = is_first_group_approver
        controller.context['is_second_group_approver'] = is_second_group_approver

    return True
