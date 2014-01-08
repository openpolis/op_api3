from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from pops.views import PersonList, PersonDetail

urlpatterns = patterns('pops.views',
                       url(r'^$', 'api_root', name='pops-api-root'),
                       url(r'^persons$', PersonList.as_view(), name='person-list'),
                       url(r'^persons/(?P<pk>\d+)$', PersonDetail.as_view(), name='person-detail'),
                       )

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

# Default login/logout views
urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
