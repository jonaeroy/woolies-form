from ferris.core import template
from google.appengine.api import mail
from google.appengine.api import app_identity


def send(recipient, subject, body, sender=None, reply_to=None, **kwargs):

    """
    Sends an html email to ``recipient`` with the given ``subject`` and ``body``.

    If sender is none, it's automatically set to ``app_config['email']['sender']``.

    Any additionally arguments are passed to ``mail.send_mail``, such as headers.
    """
    #sender = sender if sender else settings.get('email')['sender']
    sender = "notifications@" + str(app_identity.get_application_id()) + ".appspotmail.com"

    return mail.send_mail(
        sender=sender,
        to=recipient,
        subject=subject,
        body=body,
        html=body,
        reply_to=reply_to if reply_to else sender,
        **kwargs)


def send_template(recipient, subject, template_name, context=None, theme=None, **kwargs):
    """
    Renders a template and sends an email in the same way as :func:`send`.
    templates should be stored in ``/templates/email/<template>.html``.

    For example:

        mail.send(
            recipient='jondoe@example.com',
            subject='A Test Email',
            template_name='test',
            context={
                'name': 'George'
            })

    Would render the template ``/templates/email/test.html``.
    """
    name = ('email/' + template_name + '.html', template)
    context = context if context else {}
    body = template.render_template(name, context, theme=theme)
    res = send(recipient, subject, body, **kwargs)
    return res, body
