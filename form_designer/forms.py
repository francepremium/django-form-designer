from django import forms
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
    def save(self, commit=True):
        obj = super(FormCreateForm, self).save(False)
        obj.name = slugify(self.cleaned_data['verbose_name'])
        if commit:
            obj.save()
        return obj

    class Meta:
        fields = ('verbose_name',)
        model = Form


class WidgetForm(forms.ModelForm):
    class Meta:
        model = Widget
        exclude = ('tab', 'content_type', 'name', 'order')
