from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       #url(r'^pops/', include('op_api.pops.urls')),
                       url(r'^politici/', include('op_api.politici.urls')),
                       url(r'^parlamento/', include('op_api.parlamento.urls', namespace='parlamento')),
                       )

