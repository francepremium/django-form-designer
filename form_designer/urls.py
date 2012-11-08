from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from views import (FormCreateView, FormUpdateView,
        TabCreateView, TabUpdateView, TabDeleteView,
        WidgetCreateView, WidgetUpdateView, WidgetDeleteView)


urlpatterns = patterns('',
    url(r'form/create/$',
        login_required(FormCreateView.as_view()),
        name='form_designer_form_create'),
    url(r'form/(?P<pk>\d+)/update/$',
        login_required(FormUpdateView.as_view()),
        name='form_designer_form_update'),

    # Tabs
    url(r'tab/create/$',
        login_required(TabCreateView.as_view()),
        name='form_designer_tab_create'),
    url(r'tab/update/$',
        login_required(TabUpdateView.as_view()),
        name='form_designer_tab_update'),
    url(r'tab/delete/$',
        login_required(TabDeleteView.as_view()),
        name='form_designer_tab_delete'),

    # Widgets
    url(r'widget/create/$',
        login_required(WidgetCreateView.as_view()),
        name='form_designer_widget_create'),
    url(r'widget/update/$',
        login_required(WidgetUpdateView.as_view()),
        name='form_designer_widget_update'),
    url(r'widget/delete/$',
        login_required(WidgetDeleteView.as_view()),
        name='form_designer_widget_delete'),
)
