import json

from django.template import defaultfilters
from django import http
from django.utils.translation import ugettext as _
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django import shortcuts
from django.template.defaultfilters import slugify
from django.forms.models import modelform_factory

import rules_light

from forms import FormCreateForm, CreateForm, WidgetForm
from utils import import_class
from models import *
from settings import WIDGET_CLASSES


class PkUrlKwarg(SingleObjectMixin):
    """
    Take the pk from request.GET and sets it to kwargs, useful to avoid
    reversing urls from javascript
    """
    def get_object(self, *args, **kwargs):
        self.kwargs[self.pk_url_kwarg] = self.request.REQUEST['pk']
        return super(PkUrlKwarg, self).get_object(*args)


class AjaxDeleteView(generic.DeleteView):
    """ Delete and respond with 204. Only accept post requests. """
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.HttpResponse('', status=204)


class AjaxFormMixin(object):
    """ `form_valid()` respond with 204 on update, 201 on creation. """
    def form_valid(self, form):
        if form.instance.pk:
            status = 204
        else:
            status = 201

        self.object = form.save()
        return http.HttpResponse(self.object.pk, status=status)


class TabCreateView(generic.View):
    model = Tab
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        form = shortcuts.get_object_or_404(Form,
            pk=request.POST['form_pk'])

        rules_light.require(request.user, 'form_designer.form.update', form)

        tab = Tab.objects.create(
            verbose_name=request.POST['verbose_name'],
            name=slugify(request.POST['verbose_name']),
            form=form)

        return http.HttpResponse(json.dumps({'tab': {
            'pk': tab.pk, 'verbose_name': tab.verbose_name}}), status=201)


class TabSecurity(object):
    """
    Decorates `get_object()`, but checks if `request.user` has
    `form_designer.form.update` for tab.form.
    """
    def get_object(self):
        tab = super(TabSecurity, self).get_object()
        rules_light.require(self.request.user, 'form_designer.form.update',
            tab.form)
        return tab


class TabDeleteView(PkUrlKwarg, TabSecurity, AjaxDeleteView):
    model = Tab


class TabUpdateView(PkUrlKwarg, TabSecurity, generic.DetailView):
    http_method_names = ['post']
    model = Tab

    def post(self, request, *args, **kwargs):
        tab = self.get_object()
        tab.verbose_name = defaultfilters.striptags(
            request.POST['name']).strip().replace('&nbsp;', '')
        tab.save()
        return http.HttpResponse(status=204)


@rules_light.class_decorator
class FormCreateView(generic.CreateView):
    model = Form
    template_name = 'form_designer/form_create.html'
    form_class = FormCreateForm

    def get_success_url(self):
        return self.object.get_update_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(FormCreateView, self).form_valid(form)


@rules_light.class_decorator('form_designer.form.update')
class FormUpdateView(generic.DetailView):
    model = Form
    template_name = 'form_designer/form_update.html'

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
        self.object = self.get_object()

        if 'tabs' in request.POST.keys():
            i = 0
            for pk in request.POST.getlist('tabs'):
                self.object.tab_set.filter(pk=pk).update(order=i)
                i += 1

        if 'widgets' in request.POST.keys():
            i = 0
            for pk in request.POST.getlist('widgets'):
                Widget.objects.filter(tab__form=self.object, pk=pk
                    ).update(order=i)
                i += 1

        return http.HttpResponse(status=204)


class WidgetFormMixin(object):
    def get_form(self, form_class):
        pk = self.request.GET.get('pk', None)
        widget_class = self.request.GET.get('widget_class', None)

        if pk:
            self.object = Widget.objects.filter(pk=pk
                ).select_subclasses()[0]
        else:
            if widget_class not in WIDGET_CLASSES:
                return

            tab = Tab.objects.get(pk=self.request.GET['tab_id'])

            widget_class = import_class(widget_class)

            self.object = widget_class(tab=tab)

        rules_light.require(self.request.user, 'form_designer.form.update',
            self.object.tab.form)

        return self.object.configuration_form_instance(self.request)

    def get_template_names(self):
        widget_name = self.object.__class__.__name__

        return [
            'form_designer/widget_forms/%s.html' % widget_name,
            'form_designer/widget_form.html',
        ]


class WidgetCreateView(WidgetFormMixin, AjaxFormMixin, generic.CreateView):
    form_class = WidgetForm  # overridden by WidgetFormMixin.get_form


class WidgetSecurity(object):
    """
    Decorate `get_object()`, to test if user has update permission on the form.
    """
    def get_object(self):
        widget = super(WidgetSecurity, self).get_object()
        rules_light.require(self.request.user, 'form_designer.form.update',
                widget.tab.form)
        return widget


class WidgetUpdateView(PkUrlKwarg, WidgetSecurity, WidgetFormMixin,
        AjaxFormMixin, generic.UpdateView):
    model = Widget


class WidgetDeleteView(PkUrlKwarg, WidgetSecurity, AjaxDeleteView):
    model = Widget
