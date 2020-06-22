# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from api.views import ApiRootView

admin.autodiscover()

urlpatterns = patterns('',
   url(r'^$', ApiRootView.as_view(), name='op-api-root'),
   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   url(r'^admin/', include(admin.site.urls)),
#    url(r'^maps/', include('places.urls', namespace='maps')),
#   url(r'^pops/', include('pops.urls')),
   url(r'^politici/', include('politici.urls', namespace='politici')),
   url(r'^parlamento/', include('parlamento.urls', namespace='parlamento')),
   url(r'^territori/', include('territori.urls', namespace='territori')),
)

