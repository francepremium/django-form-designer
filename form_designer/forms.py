from django import forms
from django.db.models import Max
from django.template.defaultfilters import slugify

from models import *


class CreateForm(forms.Form):
    verbose_name = forms.CharField(max_length=200)

    def save(self):
        """ You must define self.model_class for this to work """
        verbose_name = self.cleaned_data['verbose_name']
        name = slugify(verbose_name)
        return self.model_class.objects.create(name=name,
                verbose_name=verbose_name)


class FormCreateForm(forms.ModelForm):
    class Meta:
        fields = ('verbose_name',)
        model = Form


class WidgetForm(forms.ModelForm):
    def save(self, commit=True):
        if not self.instance.order:
            order = self.instance.tab.widget_set.aggregate(m=Max('order'))['m']

            if order:
                order += 1
            else:
                order = 0

            self.instance.order = order

        return super(WidgetForm, self).save(commit=commit)

    class Meta:
        model = Widget
        exclude = ('tab', 'content_type', 'name', 'order')
