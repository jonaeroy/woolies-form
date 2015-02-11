import logging


class FormManager(object):

    # before template render

    def __init__(self, controller):
        self.controller = controller
        #self.controller.events.after_startup += self.get_top_level_nav
        #self.controller.events.after_startup += self.get_user_language

    def view(self, key):
        c = self.controller
        #c.context['test'] = 'TESTMUNA'

    __call__ = view

    def test(self):
        pass
