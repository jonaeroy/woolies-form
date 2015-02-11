Events
======

Ferris has a very simple global pubsub-style event system. Beyond the events emitted by :doc:`handlers`, there's also a way to globally emit and respond to events.

.. module:: ferris.core.events

listeners.py
------------

Inside of the ``app`` directory lives ``listeners.py``. This is where you can register global event listeners using ``on``:

.. autofunction:: on

For example, to make sure a user is in a particular domain::

    @on('handler_is_authorized')
    def is_authorized(handler, *args, **kwargs):
        if not 'example.com' in handler.user.email():
            raise Exception('Unauthorized')

All handler events are prefixed with ``handler_`` when broadcast globally.

Emitting Events
---------------

You can emit events on the global bus by using ``fire``:

.. autofunction:: fire

For example::

    @route
    def transmat(self, item):
        fire("item_transmat", item)
