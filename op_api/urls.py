from django.conf.urls import patterns, include, url
from django.contrib import admin
from op_api.views import ApiRootView

admin.autodiscover()

urlpatterns = patterns('',
   url(r'^$', ApiRootView.as_view(), name='op-api-root'),
   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^pops/', include('op_api.pops.urls')),
   url(r'^politici/', include('op_api.politici.urls', namespace='politici')),
   url(r'^parlamento/', include('op_api.parlamento.urls', namespace='parlamento')),
   url(r'^territori/', include('op_api.territori.urls', namespace='territori')),
)

