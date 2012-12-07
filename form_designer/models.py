from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django import forms
from django.forms.models import modelform_factory
from django.template.defaultfilters import slugify
from django.db.models import signals

from picklefield.fields import PickledObjectField
from polymodels.models import PolymorphicModel
from crispy_forms.layout import Layout, Fieldset

from utils import import_class


__all__ = ['Form', 'Tab', 'Widget',
    'InputWidget', 'TextareaWidget', 'ChoiceWidget']


class Form(models.Model):
    name = models.CharField(max_length=200)
    verbose_name = models.CharField(max_length=200)
    author = models.ForeignKey('auth.User')

    def to_crispy(self):
        layout = Layout()
        for tab in self.tab_set.all():
            layout.fields.append(tab.to_crispy())

        return layout

    def get_form_class(self, bases=None, form_class_name=None, attrs=None):
        if bases is None:
            bases = (forms.Form,)

        if form_class_name is None:
            form_class_name = 'Form%s' % self.pk

        widgets = Widget.objects.filter(tab__form=self).select_subclasses()
        attributes = {w.name: w.field_instance() for w in widgets}

        if attrs:
            attributes.update(attrs)

        form_class = type(form_class_name, bases, attributes)
        return form_class

    @property
    def fields(self):
        for tab in self.tab_set.all():
            for field in tab.field_set.all():
                yield field

    def update_from_dict(self, data):
        self.name = data[u'name'].strip()

        self.tab_set.all().delete()
        order = 0

        for tab_data in data[u'tabs']:
            tab = Tab(name=tab_data[u'name'].strip(), form=self, order=order)
            tab.update_from_dict(tab_data)
            self.tab_set.add(tab)
            order += 1

    def __unicode__(self):
        return self.name

    def get_update_url(self):
        return reverse('form_designer_form_update', args=(self.pk,))

    class Meta:
        ordering = ('name',)


class Tab(models.Model):
    name = models.CharField(max_length=200)
    verbose_name = models.CharField(max_length=200)
    form = models.ForeignKey(Form)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order', 'pk')

    def to_crispy(self):
        fieldset = Fieldset(self.name)
        for field in self.field_set.all():
            fieldset.fields.append(field.to_crispy())
        return fieldset

    def update_from_dict(self, data):
        self.fields = []
        order = 0

        for field_data in data[u'fields']:
            field = Field(
                tab=self,
                name=field_data[u'name'].strip(),
                kind=field_data[u'kind'].strip(),
                required=field_data[u'required'],
                order=order,
                verbose_name=field_data[u'verbose_name'].strip(),
                help_text=field_data[u'help_text'].strip()
            )
            field.save()
            self.field_set.add(field)
            order += 1

    def __unicode__(self):
        return self.name


class Widget(PolymorphicModel):
    tab = models.ForeignKey(Tab)
    name = models.CharField(max_length=200)
    verbose_name = models.CharField(max_length=200)
    help_text = models.TextField(blank=True)
    required = models.BooleanField()
    order = models.IntegerField()

    @property
    def configuration_form_class(self):
        """ Return the form class to configure this widget. """

        from forms import WidgetForm  # avoid recursion
        return modelform_factory(self.__class__, form=WidgetForm)

    def configuration_form_instance(self, request):
        """ Return the form instance to configure this widget. """
        form_class = self.configuration_form_class

        if request.method == 'POST':
            form = form_class(request.POST, instance=self)
        else:
            form = form_class(instance=self)

        return form

    def field_class(self):
        return import_class(self.field_class_path)

    def widget_class(self):
        return import_class(self.widget_class_path)

    def field_kwargs(self):
        return {
            'label': self.verbose_name,
            'required': self.required,
            'help_text': self.help_text,
            'widget': self.widget_class()(**self.widget_kwargs()),
        }

    def widget_kwargs(self):
        return {}

    def field_instance(self):
        return self.field_class()(**self.field_kwargs())

    def __unicode__(self):
        return self.verbose_name

    def update_url(self):
        return reverse('form_designer_widget_update', args=(self.pk,))

    @classmethod
    def create_url(self):
        return reverse('form_designer_widget_create')

    class Meta:
        ordering = ('order',)


class InputWidget(Widget):
    max_length = models.IntegerField(default=255)
    field_class_path = 'django.forms.fields.CharField'
    widget_class_path = 'django.forms.widgets.TextInput'

    def field_kwargs(self):
        kwargs = super(InputWidget, self).field_kwargs()
        kwargs['max_length'] = self.max_length
        return kwargs

    class Meta:
        verbose_name = _(u'Short text input')
        verbose_name_plural = _(u'Short text inputs')


class IntegerWidget(Widget):
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    field_class_path = 'django.forms.fields.IntegerField'
    widget_class_path = 'django.forms.widgets.TextInput'

    def field_kwargs(self):
        kwargs = super(IntegerWidget, self).field_kwargs()
        kwargs['max_value'] = self.max_value
        kwargs['min_value'] = self.min_value
        return kwargs

    class Meta:
        verbose_name = _(u'Integer input')
        verbose_name_plural = _(u'Integer inputs')


class DecimalWidget(Widget):
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    max_digits = models.IntegerField(null=True, blank=True)
    decimal_places = models.IntegerField(null=True, blank=True)
    field_class_path = 'django.forms.fields.DecimalField'
    widget_class_path = 'django.forms.widgets.TextInput'

    def field_kwargs(self):
        kwargs = super(DecimalWidget, self).field_kwargs()
        kwargs['max_value'] = self.max_value
        kwargs['min_value'] = self.min_value
        kwargs['max_digits'] = self.max_digits
        kwargs['decimal_places'] = self.decimal_places
        return kwargs

    class Meta:
        verbose_name = _(u'Decimal input')
        verbose_name_plural = _(u'Decimal inputs')


class TextareaWidget(Widget):
    field_class_path = 'django.forms.fields.CharField'
    widget_class_path = 'django.forms.widgets.Textarea'

    class Meta:
        verbose_name = _(u'Long text input')
        verbose_name_plural = _(u'Long text inputs')


class EmailWidget(Widget):
    field_class_path = 'django.forms.fields.EmailField'
    widget_class_path = 'django.forms.widgets.TextInput'

    class Meta:
        verbose_name = _(u'Email input')
        verbose_name_plural = _(u'Email inputs')


class BooleanWidget(Widget):
    field_class_path = 'django.forms.fields.BooleanField'
    widget_class_path = 'django.forms.widgets.BooleanWidget'

    class Meta:
        verbose_name = _(u'Checkbox input')
        verbose_name_plural = _(u'Checkbox inputs')


class ChoiceWidget(Widget):
    choices = PickledObjectField()
    multiple = models.BooleanField()

    class Meta:
        verbose_name = _(u'Choice select')
        verbose_name_plural = _(u'Choice selects')


def auto_name(sender, instance, **kwargs):
    if not issubclass(sender, (Form, Tab, Widget)):
        return

    if not instance.name:
        instance.name = slugify(instance.verbose_name).replace('-', '_')
signals.pre_save.connect(auto_name)


def first_tab(sender, instance, created, **kwargs):
    if not created:
        return

    instance.tab_set.create(verbose_name=instance.verbose_name)
signals.post_save.connect(first_tab, sender=Form)
