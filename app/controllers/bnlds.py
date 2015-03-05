from ferris import Controller, messages, route_with, route
from ferris.components.pagination import Pagination
from ferris.components.upload import Upload
from app.models.bnld import Bnld
import json
import datetime


class Bnlds(Controller):

    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        pagination_limit = 10
        Model = Bnld



    @route_with('/bnlds/list', methods=['GET'])
    def list(self):
        self.meta.view.template_name = 'angular/bnlds/index.html'

    @route
    def form(self):
        self.meta.view.template_name = 'angular/bnlds/bnldform.html'

    @route_with('/api/bnlds', methods=['GET'])
    def api_list(self):
        self.context['data'] = Bnld.list_all()

    @route_with('/api/bnlds', methods=['POST'])
    def api_create(self):
        params = json.loads(self.request.body)
        print repr(params)
        params['Number_of_Items'] = int(params['Number_of_Items'])
        self.context['data'] = Bnld.create(params)

    @route_with('/api/bnlds:<key>', methods=['GET'])
    def api_get(self, key):
        self.context['data'] = self.util.decode_key(key).get()

    @route_with('/api/bnlds/:<key>', methods=['POST'])
    def api_update(self, key):
        temp_params = json.loads(self.request.body)
        params = {'Buyer_or_BAA_Name': temp_params['Buyer_or_BAA_Name'],
                  'Merchandise_Manager':temp_params['Merchandise_Manager'],
                  'Number_of_Items': int(temp_params['Number_of_Items']),
                  'All_New_Lines_Passed_Validation': temp_params['All_New_Lines_Passed_Validation'],
                  'QA_Acceptance': temp_params['QA_Acceptance'],
                  'MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines': temp_params['MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines'],
                  'Include_Any_Comments_Below': temp_params['Include_Any_Comments_Below']
        }
        bnld = self.util.decode_key(key).get()
        bnld.update(params)
        self.context['data'] = bnld

    @route_with('/api/bnlds/:<key>', methods=['DELETE'])
    def api_delete(self, key):
        bnld = self.util.decode_key(key).get()
        bnld.delete()
        return 200

    @route_with('/api/get_user', methods=['GET'])
    def api_get_user(self):
        msg = CurrentUser(email= self.session.get('user_email'))
        self.context['data'] = msg


class CurrentUser(messages.Message):
    email = messages.StringField(1)

