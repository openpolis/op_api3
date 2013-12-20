# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from places.views import MapsView, PlaceListView, PlaceDetailView, PlaceTypeDetailView, PlaceTypeListView, IdentifierListView, \
    IdentifierDetailView, LanguageDetailView, LanguageListView, ClassificationListView, \
    ClassificationDetailView, ClassificationNodeDetailView

__author__ = 'guglielmo'

urlpatterns = patterns('places.views',
   url(r'^$', MapsView.as_view(), name='api-root'),
   url(r'^places$', PlaceListView.as_view(), name='place-list'),
   url(r'^places/(?P<slug>[\w-]+)$', PlaceDetailView.as_view(), name='place-detail'),
   url(r'^placetypes$', PlaceTypeListView.as_view(), name='placetype-list'),
   url(r'^placetypes/(?P<slug>[\w-]+)$', PlaceTypeDetailView.as_view(), name='placetype-detail'),
   url(r'^classifications$', ClassificationListView.as_view(), name='classification-list'),
   url(r'^classifications/(?P<slug>[\w-]+)$', ClassificationDetailView.as_view(), name='classification-detail'),
   url(r'^classifications/(?P<tag__slug>[\w-]+)/places/(?P<place__slug>[\w-]+)$',
       ClassificationNodeDetailView.as_view(), name='classificationnode-detail'),
   url(r'^identifiers$', IdentifierListView.as_view(), name='identifier-list'),
   url(r'^identifiers/(?P<slug>[\w-]+)$', IdentifierDetailView.as_view(), name='identifier-detail'),
   url(r'^languages$', LanguageListView.as_view(), name='language-list'),
   url(r'^languages/(?P<iso639_1_code>\w+)$', LanguageDetailView.as_view(), name='language-detail'),

)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
