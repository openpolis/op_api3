from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from op_api.politici.views import UserList, UserDetail, PoliticianList, PoliticianDetail, InstitutionList, ChargeTypeList, InstitutionChargeList, InstitutionChargeDetail, InstitutionDetail, ChargeTypeDetail

__author__ = 'guglielmo'

urlpatterns = patterns('op_api.politici.views',
   url(r'^$', 'api_root', name='politici-api-root'),
   url(r'^users$', UserList.as_view(), name='politici-user-list'),
   url(r'^users/(?P<pk>\d+)$', UserDetail.as_view(), name='politici-user-detail'),
   url(r'^politicians$', PoliticianList.as_view(), name='politici-politician-list'),
   url(r'^politicians/(?P<pk>\d+)$', PoliticianDetail.as_view(), name='politici-politician-detail'),
   url(r'^instcharges$', InstitutionChargeList.as_view(), name='politici-instcharge-list'),
   url(r'^instcharges/(?P<pk>\d+)$', InstitutionChargeDetail.as_view(), name='politici-instcharge-detail'),
   url(r'^institutions$', InstitutionList.as_view(), name='politici-institution-list'),
   url(r'^institutions/(?P<pk>\d+)$', InstitutionDetail.as_view(), name='politici-institution-detail'),
   url(r'^chargetypes$', ChargeTypeList.as_view(), name='politici-chargetype-list'),
   url(r'^chargetypes/(?P<pk>\d+)$', ChargeTypeDetail.as_view(), name='politici-chargetype-detail'),

)

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
