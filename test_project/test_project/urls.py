from django.conf.urls import patterns, include, url

import rules_light
rules_light.autodiscover()

from django.contrib import admin

js_info_dict = {
    'packages': ('form_designer',),
}


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^test_project/', include('test_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^form_designer/', include('form_designer.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog',
        {'packages': ('form_designer',)}),
)
