import json

from django import http
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django import shortcuts
from django.template.defaultfilters import slugify

from forms import FormCreateForm, CreateForm, WidgetUpdateForm
from utils import import_class
from models import *
from settings import WIDGET_CLASSES


class PkUrlKwarg(SingleObjectMixin):
    """
    Take the pk from request.GET and sets it to kwargs, useful to avoid
    reversing urls from javascript
    """
    def get_object(self, queryset=None):
        self.kwargs[self.pk_url_kwarg] = self.request.REQUEST['pk']
        return super(PkUrlKwarg, self).get_object(queryset)


class AjaxDeleteView(generic.DeleteView):
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.HttpResponse('', status=204)


class TabSecurity(object):
    """
    Return a queryset of Tab that have a form which author is request.user.
    For security.
    """
    def get_queryset(self):
        return Tab.objects.filter(form__author=self.request.user)


class TabCreateView(generic.View):
    model = Tab
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        form = shortcuts.get_object_or_404(Form,
            author=self.request.user, pk=request.POST['form_pk'])

        tab = Tab.objects.create(
            verbose_name=request.POST['verbose_name'],
            name=slugify(request.POST['verbose_name']),
            form=form)

        return http.HttpResponse(json.dumps({'tab': {
            'pk': tab.pk, 'verbose_name': tab.verbose_name}}), status=201)


class TabDeleteView(PkUrlKwarg, TabSecurity, AjaxDeleteView):
    pass


class TabUpdateView(PkUrlKwarg, TabCreateView, generic.DetailView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        pass


class FormCreateView(generic.CreateView):
    model = Form
    template_name = 'form_designer/form_create.html'
    form_class = FormCreateForm

    def get_success_url(self):
        return self.object.get_update_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(FormCreateView, self).form_valid(form)



class FormUpdateView(generic.DetailView):
    template_name = 'form_designer/form_update.html'
    model = Form

    def get_context_data(self, *args, **kwargs):
        widget_classes = {}

        for widget_class_path in WIDGET_CLASSES:
            widget_class = import_class(widget_class_path)
            widget_class.META = widget_class._meta
            widget_classes[widget_class_path] = widget_class

        return {
            'widget_classes': widget_classes,
            'form': self.get_object(),
        }


class WidgetCreateView(generic.CreateView):
    form_class = CreateForm

    def get_form_class(self):
        form_class = super(WidgetCreateView, self).get_form_class()
        form_class.model_class = import_class(request.GET['widget_class'])
        assert issubclass(form_class.model_class, Widget)
        return form_class


class WidgetUpdateView(generic.UpdateView):
    form_class = WidgetUpdateForm


class WidgetDeleteView(generic.DeleteView):
    def get_object(self):
        pass
