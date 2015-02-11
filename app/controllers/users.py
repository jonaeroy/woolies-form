from ferris import Controller, scaffold, route_with, route
from google.appengine.api import users
from google.appengine.ext import ndb
from ..models.user import User
import logging, pickle
#from plugins import directory
from google.appengine.api import memcache
from plugins import service_account
from google.appengine.api import taskqueue


class Users(Controller):
    class Meta:
        prefixes = ('api',)
        components = (scaffold.Scaffolding,)
       # Model = 'Users'

    class Scaffold:
        display_properties = ('email', 'fullname', 'group', 'role')
        #model = user

    def adminonly(fn):
        def check(fn):
            if users.is_current_user_admin():
                return fn
            else:
                return False

        return check

    #list = scaffold.list
    def list(self):
        self.context['data'] = User.all()
        self.context['PAGE_TITLE'] = 'Manage Users'

    view = scaffold.view
    delete = scaffold.delete

    def check_email_if_exist(self, email):
        query = User.query().filter(User.email==email)
        check = query.fetch()
        if check:
            raise NameError('Email already exist!')


    def add(self):
        def before_save(controller, container, item):
            email = str(item.email).lower()
            self.check_email_if_exist(email)
            item.email = email


        self.events.scaffold_before_save += before_save
        return scaffold.add(self)

    def edit(self, key):
        def before_save(controller, container, item):
            email = str(item.email).lower()
            item.email = email

        self.events.scaffold_before_save += before_save
        return scaffold.edit(self, key)

    @route_with(template='/users/get/<group_key>')
    def get_user_list(self, group_key):

        query = self.get_users_by_group(group_key)
        return self.util.stringify_json(query)

    @classmethod
    def get_users_by_group(self, group_key):
        group_key = ndb.Key(urlsafe=group_key)
        query = User.query(User.group == group_key).order(User.email)
        return query

    @classmethod
    def get_user_list_by_group(self, group_key):
        query = self.get_users_by_group(group_key)
        users = query.fetch()
        emails = ''

        for user in users:
            emails += user.email + "; "
        return str(emails)

    @classmethod
    def is_email_within_group(cls, email, group_key):
        query = cls.get_users_by_group(group_key)
        users = query.fetch()

        for user in users:
            if  (user.email == email):
                return True

        return False


    @route_with(template='/users/group/add/<email>/<name>/<group_key>')
    def add_group_member(self, email, name, group_key):

        error = False
        errorMessage = ''
        email = str(email).lower()
        exist = User.query().filter(User.email==email).get()

        if exist:
            new_group = ndb.Key(urlsafe=group_key)
            groups = exist.group

            match = False
            for group in groups:
                if new_group == group:
                    match = True
                    error = True
                    errorMessage = str(email) + " already exist in the Group."
                    break

            if not match:
                groups.append(new_group)
                exist.group = groups
                exist.put()

        else:
            group_key = ndb.Key(urlsafe=group_key)
            new_member = User(email = email,
                    fullname= name,
                    group=[group_key],
                    role='None')
            new_member.put()

        if not error:
            result = {'success': 'true'}
        else:
            result = {'success': 'false', "message" : errorMessage}

        return self.util.stringify_json(result)

    @route_with(template='/users/directory/task')
    def get_directory_users_task(self):
        q = taskqueue.Queue('default')
        q.purge()

        taskqueue.add(url='/users/directory/all', method='GET')
        return ""

    @route_with(template='/users/directory/all')
    def get_directory_users(self):
        user_list = directory.get_all_users_cached();
        logging.info("User cached return result : %s:users ==========> %s", service_account.get_config()['domain'], user_list)
        logging.info("User String Lenght =====> %s", len(user_list))
        return self.util.stringify_json(user_list);

    @classmethod
    def store(self, key, value, chunksize=950000):
        serialized = pickle.dumps(value, 2)
        values = {}
        for i in xrange(0, len(serialized), chunksize):
            values['%s.%s' % (key, i//chunksize)] = serialized[i : i+chunksize]
            memcache.set_multi(values)

    @classmethod
    def retrieve(self, key):
        result = memcache.get_multi(['%s.%s' % (key, i) for i in xrange(32)])
        serialized = ''.join([v for k, v in sorted(result.items()) if v is not None])
        return pickle.loads(serialized)

    @route
    def batch_update(self):
        results = User.query().fetch()

        for result in results:
            try:
                bc = result.banner_category
            except:
                bc = None

            # If banner category is None update the record to Default None value
            if bc is None:
                entity = result.key.get()
                entity.banner_category = None
                entity.put()

        return "Done"
