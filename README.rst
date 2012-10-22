Models
======

Each model has both a ``name`` and a ``verbose_name``. The ``name`` is auto
generated and should not be altered. It is intended to use by your
program. The ``verbose_name`` may change and is intended to use by the
end user.

Form
    Each form is saved in a Form model. It is able to return a
    django-crispy-forms layout.

Tab
    Each tab has a form.

Widget
    The base class for all widget models. It is able to instanciate
    its form field and widget.
