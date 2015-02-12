from ferrisnose import FerrisAppTest
from app.models.bnld import Bnld

class TestBnld(FerrisAppTest):

    def setUp(self):
        #super(self.__class__, self).setUp()
        
        params = {'Buyer_or_BAA_Name':  'Test',
                  'Merchandise_Manager': 'Test',
                  'Number_of_Items': 2,
                  'All_New_Lines_Passed_Validation':'Yes',
                  'QA_Acceptance': 'Yes',
                  'MSDS_Report_Loaded_onto_Chemwatch_for_all_Applicable_Lines': 'Yes'
        }

        self.bnld = Bnld.create(params)


    def testCreate(self):
        self.assertEqual(self.bnld.Buyer_or_BAA_Name, 'Test')
        self.assertEqual(self.bnld.Merchandise_Manager, 'Test')
        