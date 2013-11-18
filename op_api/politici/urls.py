from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from op_api.politici.views import UserList, UserDetail, PoliticianList, PoliticianDetail, InstitutionList, ChargeTypeList, InstitutionChargeList, InstitutionChargeDetail, InstitutionDetail, ChargeTypeDetail, PoliticiView

__author__ = 'guglielmo'

urlpatterns = patterns('op_api.politici.views',
   url(r'^$', PoliticiView.as_view(), name='api-root'),
   url(r'^users$', UserList.as_view(), name='user-list'),
   url(r'^users/(?P<pk>\d+)$', UserDetail.as_view(), name='user-detail'),
   url(r'^politicians$', PoliticianList.as_view(), name='politician-list'),
   url(r'^politicians/(?P<pk>\d+)$', PoliticianDetail.as_view(), name='politician-detail'),
   url(r'^instcharges$', InstitutionChargeList.as_view(), name='instcharge-list'),
   url(r'^instcharges/(?P<pk>\d+)$', InstitutionChargeDetail.as_view(), name='instcharge-detail'),
   url(r'^institutions$', InstitutionList.as_view(), name='institution-list'),
   url(r'^institutions/(?P<pk>\d+)$', InstitutionDetail.as_view(), name='institution-detail'),
   url(r'^chargetypes$', ChargeTypeList.as_view(), name='chargetype-list'),
   url(r'^chargetypes/(?P<pk>\d+)$', ChargeTypeDetail.as_view(), name='chargetype-detail'),

)

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
