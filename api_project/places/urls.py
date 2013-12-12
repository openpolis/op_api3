# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from places.views import PlacesView, PlaceList, PlaceDetail, PlaceTypeDetail, PlaceTypeList, IdentifierListView, \
    IdentifierDetailView, LanguageDetailView, LanguageListView

__author__ = 'guglielmo'

urlpatterns = patterns('places.views',
   url(r'^$', PlacesView.as_view(), name='api-root'),
   url(r'^places$', PlaceList.as_view(), name='place-list'),
   url(r'^places/(?P<slug>[\w-]+)$', PlaceDetail.as_view(), name='place-detail'),
   url(r'^placetypes$', PlaceTypeList.as_view(), name='placetype-list'),
   url(r'^placetypes/(?P<slug>[\w-]+)$', PlaceTypeDetail.as_view(), name='placetype-detail'),
   url(r'^identifiers$', IdentifierListView.as_view(), name='identifier-list'),
   url(r'^identifiers/(?P<slug>[\w-]+)$', IdentifierDetailView.as_view(), name='identifier-detail'),
   url(r'^languages$', LanguageListView.as_view(), name='language-list'),
   url(r'^languages/(?P<iso639_1_code>\w+)$', LanguageDetailView.as_view(), name='language-detail'),

)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
