from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from parlamento import views

__author__ = 'daniele'


urls = [
    url(r'^groups$', views.GruppoListView.as_view(), name='gruppo-list'),
    url(r'^groups/(?P<gruppo>[\w_.-]+)$', views.GruppoDetail.as_view(), name='gruppo-detail'),
    url(r'^districts$', views.CircoscrizioneListView.as_view(), name='circoscrizione-list'),
    url(r'^districts/(?P<circoscrizione>[\w_.-]+)$', views.CircoscrizioneDetailView.as_view(), name='circoscrizione-detail'),

    # old views
    url(r'^parliamentarians-cache$', views.ParlamentareCacheListView.as_view(),
        name='parlamentare-cache-list'),
    url(r'^parliamentarians-cache/(?P<politician_id>[0-9]+)$',
        views.ParlamentareCacheDetailView.as_view(),
        name='parlamentare-cache-detail'),

    url(r'^parliamentarians$',
        views.ParlamentareListView.as_view(),
        name='parlamentare-list'),
    url(r'^parliamentarians/(?P<politician_id>[0-9]+)$',
        views.ParlamentareDetailView.as_view(),
        name='parlamentare-detail'),

    url(r'^sites$', views.SedeListView.as_view(), name='sede-list'),
    url(r'^charges$', views.CaricaListView.as_view(), name='carica-list'),
    url(r'^sittings$', views.SedutaListView.as_view(), name='seduta-list'),
    url(r'^sittings/(?P<seduta>[0-9]+)$', views.SedutaDetailView.as_view(), name='seduta-detail'),
    url(r'^votes$', views.VotazioneListView.as_view(), name='votazione-list'),
    url(r'^votes/(?P<votazione>[0-9]+)$', views.VotazioneDetailView.as_view(), name='votazione-detail'),
]

urlpatterns = [
    url(r'^$', views.LegislaturaListView.as_view(), name='legislatura-list'),
    url(r'^(?P<legislatura>[0-9]+)$', views.LegislaturaDetailView.as_view(), name='legislatura-detail'),
    url(r'^(?P<legislatura>[0-9]+)/', include(urls))
]

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])

