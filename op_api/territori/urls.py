from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from op_api.territori.views import LocationList, LocationTypeList, LocationDetail

__author__ = 'guglielmo'

urlpatterns = patterns('op_api.territori.views',
   url(r'^$', 'api_root', name='territori-api-root'),
   url(r'^locations$', LocationList.as_view(), name='territori-location-list'),
   url(r'^locations/(?P<pk>\d+)$', LocationDetail.as_view(), name='territori-location-detail'),
   url(r'^locationtypes$', LocationTypeList.as_view(), name='territori-locationtype-list'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
