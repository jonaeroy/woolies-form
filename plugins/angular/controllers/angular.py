from ferris import Controller, route_with

class Angular(Controller):

    @route_with(template='/ng-view<name:.*>')
    def show(self, name):


        # initialize values for angular variables and
        # in order for search page to be available to all

        self.meta.view.template_name = 'angular/main.html'
