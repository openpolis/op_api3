from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from politici.views import UserList, UserDetail

urlpatterns = patterns('politici.views',
                       url(r'^$', 'api_root', name='politici-api-root'),
                       url(r'^users$', UserList.as_view(), name='opuser-list'),
                       url(r'^users/(?P<pk>\d+)$', UserDetail.as_view(), name='opuser-detail'),
                       )

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

# Default login/logout views
urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
