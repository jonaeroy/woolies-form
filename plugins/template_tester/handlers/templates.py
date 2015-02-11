from ferris.core.handler import Handler, route


class Templates(Handler):

    def list(self):
        pass

    @route
    def render(self):
        theme = self.request.params.get('theme', None)
        template = self.request.params.get('template', None)

        self.theme = theme
        self.template_name = template
