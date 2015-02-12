from ferrisnose import FerrisAppTest

class TestBnlds(FerrisAppTest):
    
    jpost = lambda self, url, params: self.testapp.post_json(url, params).json

    def setUp(self):
        #super(self.__class__,self).setUp()
        #self.loginUser(email=self.login_email, admin=True)

        params = {'Buyer_or_BAA_Name':  'Test',
                  'Merchandise_Manager': 'Test',
                  'Number_of_Items': 2,
                  'All_New_Lines_Passed_Validation':'Yes',
                  'QA_Acceptance': 'Yes',
                  'MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines': 'Yes'
              }
        self.bnlds = self.jpost('/api/bnlds', params).json

    def testCreate(self):
        assert self.bnlds['Buyer_or_BAA_Name'] == 'Test'

