Forms
=====

Ferris uses the excellent `wtforms <http://wtforms.simplecodes.com/docs/1.0.2/>`_ library. Please consult the wtforms documentation for a list of field types and advanced form usage. We will cover how to use forms in conjuction with Ferris.

.. module:: ferris.core.forms

Using Forms in Handlers
-----------------------

Once you have a form class, you can process form data into your form using the ``process_form_data`` function:

.. automethod:: ferris.core.handler.Handler.process_form_data

For example::

    def contact_us(self):
        form = ContactUsForm()
        self.process_form_data(form)

        if self.request.method != 'GET' and form.validate():
            return form.message

Using Forms in Views
--------------------

Since Ferris uses Jinja2 and wtforms, all of the same principles in the wtforms documentation apply.

Ferris does however provide one useful macro in ``macros/form.html``:

.. function:: form_control(field, container_element='div')

    Generates a bootstrap style form control with error message and help block.

For example::

    {% import "macros/form.html" as f with context %}

    <form>
        {{f.form_control(form.title)}}
        {{f.form_control(form.description)}}
    </form>

Model Form
----------

Usually you'll be using forms to interact with model data. In Ferris, this sort of use is called a *Model Form*, a model can have any number of forms (for example, different forms for different workflow steps).

You can generate a model form automatically using ``model_form``:

.. autofunction:: model_form

For example::

    CatInfoForm = model_form(Cat)

This is exactly what :doc:`scaffolding` does if you do not specify a model form.

You can also add additional fields to your form just like any other form::

    class CatInfoForm(model_form(Cat)):
        claws = wtforms.fields.BooleanField()

When using :doc:`scaffolding`, you can specify the Model Form to use by setting :attr:`~ferris.core.scaffolding.ScaffoldHandler.ModelForm`.

For example::

    @scaffold
    def Cats(Handler):
        ModelForm = CatInfoForm

or::

    def add(self):
        self.ModelForm = CatInfoForm
        return self.scaffold.add(self)
