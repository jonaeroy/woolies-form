from ferris import Controller, route, route_with
from ..models.woolies_form import WooliesForm
from plugins import directory
from google.appengine.api import memcache
from ..models.user import User
from google.appengine.api import users
from ferris.core.ndb import BasicModel
from ..controllers.utils import Utils

from google.appengine.ext.ndb import FilterNode
from ..models.leaveapp import Leaveapp
from ..models.bnld import Bnld
from ..models.bws_store import BwsStore

#import google.appengine.ext.db

import logging
import json


class Mains(Controller):
    listOfStatuses = ["Pending Approval", "Temporarily Approved", "Approved", "Rejected"]

    class Meta:
        prefixes = ('admin', 'api')
        #components = (FormManager)

    class FormStats:

        def __init__(self,
                     formListId,
                     query,
                     queryApproverFilter,
                     statusFilter):
            self.query = query
            self.queryApproverFilter = queryApproverFilter
            self.statusFilter = statusFilter
            self.formListId = formListId
            self.isApprover = False
            self.formDescription = ""
            self.numberOfActions = 0
            self.statusCounts = [0, 0, 0, 0]

        def locatedData(self):
            if (self.numberOfActions > 0):
                return True

            for statusCount in self.statusCounts:
                if (statusCount > 0):
                    return True

            return False

    @route
    def dashboard(self):
        self.context['PAGE_TITLE'] = 'Dashboard'

        user_group = self.session.get('user_group')
        is_approver = False
        is_admin = False
        woolies_forms = WooliesForm.all()

        user_email = self.session.get('user_email')
        user_from_directory = memcache.get('%s:users' % user_email)
        logging.info("user_from_directory==========> %s", user_from_directory)
        if user_from_directory is not None:
            self.context['user_directory_givenName'] = user_from_directory.get('name').get('givenName')
            self.context['user_directory_fullname'] = user_from_directory.get('name').get('fullName')
        else:

            user_from_directory = directory.get_user_by_email(user_email)
            logging.info("user_from_directory==> %s" % user_from_directory)
            if user_from_directory:
                if not memcache.add('%s:users' % user_email, user_from_directory, 60000):
                    logging.error('Memcache set failed.')
                try:
                    self.context['user_directory_givenName'] = user_from_directory['givenName']
                    self.context['user_directory_fullname'] = user_from_directory['fullName']
                except:
                    self.context['user_directory_givenName'] = None
                    self.context['user_directory_fullname'] = None

        if user_group is not None:
            for forms in woolies_forms:
                for group in user_group:
                    if forms.first_level_manager == group:
                        is_approver = True
                        break
                    if forms.second_level_manager == group:
                        is_approver = True
                        break

            for forms in woolies_forms:
                for group in user_group:
                    if forms.form_administrator == group:
                        is_admin = True
                        break

        self.context['user_isFormApprover'] = is_approver
        self.context['user_isFormAdmin'] = is_admin

        statusText = "Pending Approval"

        current_user_email  = str(users.get_current_user().email()).lower()
        pending_status_code = Utils.revertStatus(statusText)

        if (isinstance(pending_status_code, int) != True):
            raise Exception("Status text: [%s] failed to be converted to a valid value." % (statusText,))


        listOfFormStats = []

        listOfFormStats.append(Mains.FormStats(formListId="bnlds",                         \
                                               query=Bnld.query(),                         \
                                               queryApproverFilter="Merchandise_Manager",  \
                                               statusFilter="Status"))


        listOfFormStats.append(Mains.FormStats(formListId="bws_stores",                    \
                                               query=BwsStore.query(),                     \
                                               queryApproverFilter=None,                   \
                                               statusFilter="status"))


        listOfFormStats.append(Mains.FormStats(formListId="leaveapps",                     \
                                               query=Leaveapp.query(),                     \
                                               queryApproverFilter="Line_Manager",         \
                                               statusFilter="Status"))

        # Provide access to stats data for the UI
        self.context["formStats"] = listOfFormStats


        user_group = self.session.get('user_group')


        # for each form status object query the number of enteries that match the current user
        for formStats in listOfFormStats:

            # Locate the form description and the approver groups
            for form in woolies_forms:
                if  (form.list_url == formStats.formListId):
                    formStats.formDescription = form.name

                    if user_group:
                        for groupKey in user_group:
                            if  (groupKey in [form.first_level_manager, form.second_level_manager]):
                                formStats.isApprover = True
                                break

                    break


            if  (formStats.queryApproverFilter != None):
                # Collect requests that have the current user still to approve.
                filteredQuery = formStats.query.filter(FilterNode(formStats.queryApproverFilter,  "=", current_user_email))   \
                                               .filter(FilterNode(formStats.statusFilter,         "=", pending_status_code))

                formStats.numberOfActions = filteredQuery.count()

            elif  (formStats.isApprover):
                # The current user is an approver so any requests in the pending status will require action
                filteredQuery = formStats.query.filter(FilterNode(formStats.statusFilter,    "=", pending_status_code))

                formStats.numberOfActions = filteredQuery.count()


            # For each of the status values query the number of matching values for the current user for each of the statuses
            for statusIndex in range(len(self.listOfStatuses)):
                 statusText = self.listOfStatuses[statusIndex]

                 # Convert the status text to the Id stored within the data.
                 statusCode = Utils.revertStatus(statusText)

                 if  (isinstance(statusCode, int) != True):
                     raise Exception("Status text: [%s] failed to be converted to a valid value." % (statusText,))


                 # For the current status code find the number of requests that the current user has instigated.
                 filteredQuery = formStats.query.filter(BasicModel.created_by == users.User(email=current_user_email)) \
                                                .filter(FilterNode(formStats.statusFilter, "=", statusCode))

                 # Store the result value into the array that aligns to the statuses we are checking
                 formStats.statusCounts[statusIndex] = filteredQuery.count()


    @route
    def get_in_process_forms(self):
        from ..models.bnld import Bnld
        from ..models.bws_store import BwsStore
        from ..models.director_request import DirectorRequest
        from ..models.leaveapp import Leaveapp
        from ..models.maintenance_request import MaintenanceRequest
        from ..models.multiple_change import MultipleChange
        from ..models.pack_size import PackSize
        #from ..models.qasubmission import Qasubmission
        #from ..models.replenishment import Replenishment
        from ..models.salarysacrifice import Salarysacrifice
        #from ..models.stockreject import Stockreject
        from ..models.teststore import Teststore
        from ..models.training_request import TrainingRequest
        from ..models.travel_authorisation import TravelAuthorisation

        forms = ['Bnld', 'BwsStore', 'DirectorRequest', 'Leaveapp',
                    'MaintenanceRequest', 'MultipleChange', 'PackSize',
                    'Salarysacrifice', 'TrainingRequest', 'TravelAuthorisation']

        all_result = []
        for form in forms:
            logging.info(form)
            #result = Bnld.query().filter(Bnld.Status==1)
            try:
                result = eval(form + '.query().filter('+ form +'.Status==1)')
            except:
                #logging.info(TypeError)
                try:
                    result = eval(form + '.query().filter('+ form +'.status==1)')
                except:
                    try:
                        result = eval(form + '.query().filter('+ form +'.Status=="1")')
                    except:
                        result = eval(form + '.query().filter('+ form +'.status=="1")')

            all_result.append(result)

        return self.util.stringify_json(all_result)

    @route
    def sample(self):
        pass

    @route_with(template='/update/favorites')
    def star_toggle(self):
        key = self.request.get('key')
        current_user = users.get_current_user().email()

        userinfodict = directory.get_user_by_email(current_user)

        # logging.info('========> userinfodict %s' % str(userinfodict))

        if userinfodict:
            user_fullname = userinfodict.get('name').get('fullName')
        else:
            user_fullname = 'Firstname Lastname'

        entity = User.create(current_user, user_fullname)

        flag = "False"
        status = "Unknown"

        try:
            _list = json.loads(entity.favorites)
        except:
            _list = []

        if key not in _list:
            _list.append(key)
            flag = "True"
            status = "Added"
        else:
            _list.remove(key)
            flag = "True"
            status = "Removed"

        if flag == "True":
            new_list = json.dumps(_list)
            entity.favorites = new_list
            entity.put()

        return str(status)
