from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from op_api.politici.views import UserList, UserDetail, PoliticianList, PoliticianDetail

__author__ = 'guglielmo'

urlpatterns = patterns('op_api.politici.views',
   url(r'^$', 'api_root', name='politici-api-root'),
   url(r'^users$', UserList.as_view(), name='politici-user-list'),
   url(r'^users/(?P<pk>\d+)$', UserDetail.as_view(), name='politici-user-detail'),
   url(r'^politicians$', PoliticianList.as_view(), name='politici-politician-list'),
   url(r'^politicians/(?P<pk>\d+)$', PoliticianDetail.as_view(), name='politici-politician-detail'),
)

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
