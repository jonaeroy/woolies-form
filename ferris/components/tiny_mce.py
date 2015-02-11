import wtforms


class TinyMce(object):
    """
    Automatically makes TextProperty fields into TinyMCE editors (for the admin interface
    """

    def __init__(self, controller):
        self.controller = controller
        self.controller.events.before_render += self.before_render.__get__(self)

    def before_render(self, controller, *args, **kwargs):
        form = controller.context.get('form', None)
        if form and isinstance(form, (wtforms.Form)):
            for field in form:
                if isinstance(field, wtforms.fields.simple.TextAreaField):
                    field.flags.tinymce = True
