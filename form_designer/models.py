from importlib import import_module

from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from picklefield.fields import PickledObjectField
from polymodels.models import PolymorphicModel
from crispy_forms.layout import Layout, Fieldset


class Form(models.Model):
    name = models.CharField(max_length=200)
    verbose_name = models.CharField(max_length=200)
    author = models.ForeignKey('auth.User')

    def to_crispy(self):
        layout = Layout()
        for tab in self.tab_set.all():
            layout.fields.append(tab.to_crispy())

        return layout

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

    class Meta:
        ordering = ('name',)


class Tab(models.Model):
    name = models.CharField(max_length=200)
    verbose_name = models.CharField(max_length=200)
    form = models.ForeignKey(Form)

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
    help_text = models.TextField()
    required = models.BooleanField()
    order = models.IntegerField()

    def _import(self, path):
        bits = path.split('.')
        module = bits[:-1]
        cls = bits[-1]
        module = import_module(module)
        return getattr(module, cls)

    def field_class(self):
        return self._import(self.field_class)

    def widget_class(self):
        return self._import(self.widget_class)

    def field_kwargs(self):
        return {
            'label': self.name,
            'required': self.required,
            'help_text': self.help_text,
        }

    def widget_kwargs(self):
        return {}

    def formfield_instance(self):
        return self.formfield_class()(
            widget=self.widget_class()(**self.widget_kwargs()),
            **self.formfield_kwargs())

    def __unicode__(self):
        return self.verbose_name


class InputWidget(Widget):
    max_length = models.IntegerField()
    field_class = 'django.forms.fields.CharField'
    widget_class = 'django.forms.widgets.InputWidget'

    class Meta:
        verbose_name = _(u'Short text input')
        verbose_name_plural = _(u'Short text inputs')


class TextareaWidget(Widget):
    field_class = 'django.forms.fields.CharField'
    widget_class = 'django.forms.widgets.TextareaWidget'

    class Meta:
        verbose_name = _(u'Long text input')
        verbose_name_plural = _(u'Long text inputs')


class ChoiceWidget(Widget):
    choices = PickledObjectField()
    multiple = models.BooleanField()

    class Meta:
        verbose_name = _(u'Choice select')
        verbose_name_plural = _(u'Choice selects')
