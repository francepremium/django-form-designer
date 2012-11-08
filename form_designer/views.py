import json

from django.template import defaultfilters
from django import http
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django import shortcuts
from django.template.defaultfilters import slugify

from forms import FormCreateForm, CreateForm, WidgetForm
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


class TabUpdateView(PkUrlKwarg, TabSecurity, generic.DetailView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        tab = self.get_object()
        tab.verbose_name = defaultfilters.striptags(request.POST['name']).strip(
            ).replace('&nbsp;', '')
        tab.save()
        return http.HttpResponse(status=204)


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

    def post(self, request, *args, **kwargs):
        if 'tabs' in request.POST.keys():
            i = 0
            for pk in request.POST.getlist('tabs'):
                print self.get_object().tab_set.filter(pk=pk)
                print i
                self.get_object().tab_set.filter(pk=pk).update(order=i)
                i += 1

        return http.HttpResponse(status=204)


class WidgetCreateView(generic.CreateView):
    template_name = 'form_designer/widget_form.html'
    form_class = WidgetForm

    def get_form(self, form_class):
        if self.request.GET['widget_class'] not in WIDGET_CLASSES:
            return

        widget_class = import_class(self.request.GET['widget_class'])

        widget = widget_class(tab=Tab.objects.get(  # basic security for now
            pk=self.request.GET['tab_id'], form__author=self.request.user))

        if hasattr(widget_class, 'get_configuration_form'):
            form = widget.get_configuration_form(self)
        else:
            kwargs = self.get_form_kwargs()
            kwargs.update({'instance': widget})
            form = WidgetForm(**kwargs)

        return form

    def form_valid(self, form):
        self.object = form.save()
        return http.HttpResponse(self.object.pk, status=201)


class WidgetUpdateView(generic.UpdateView):
    form_class = WidgetForm


class WidgetDeleteView(generic.DeleteView):
    def get_object(self):
        pass
