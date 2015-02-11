from ferris import Controller, route_with

class Angular(Controller):

    @route_with(template='/ng-view<name:.*>')
    def show(self, name):
        if self.context.get('user_role') in ['SYSTEM_ADMINISTRATOR', 'ADMINISTRATOR', 'SUPERVISOR', 'SHIFT_LEADER']:
            self.context['is_sysad'] = True
        if self.context.get('user_role') in ['SYSTEM_ADMINISTRATOR', 'ADMINISTRATOR', 'SUPERVISOR']:
            self.context['is_supadmins'] = True
        if self.context.get('user_role') == 'SYSTEM_ADMINISTRATOR':
            self.context['is_system_admin'] = True
        if self.context.get('user_role') == 'SHIFT_LEADER':
            self.context['is_shiftleader'] = True
        if self.context.get('user_role') == 'DISPATCHER':
            self.context['is_dispatcher'] = True
        if self.context.get('user_role') == 'CSR':
            self.context['is_csr'] = True

        # initialize values for angular variables and
        # in order for search page to be available to all
        self.context['data'] = {'selected_order': '', 'active_trips': ''}
        self.meta.view.template_name = 'angular/ui.html'
