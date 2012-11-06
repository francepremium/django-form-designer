from django.conf import settings


WIDGET_CLASSES = getattr(settings, 'FORM_DESIGNER_WIDGET_CLASSES', (
    'form_designer.models.InputWidget',
    'form_designer.models.TextareaWidget',
    'form_designer.models.ChoiceWidget',
))
