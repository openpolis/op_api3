from django.conf.urls import patterns, include, url
from parlamento import views

__author__ = 'daniele'


urls = (
    url(r'^gruppi/$', views.GruppoListView.as_view(), name='gruppo-list'),
    url(r'^gruppi/(?P<gruppo>[\w_.-]+)/$', views.GruppoDetail.as_view(), name='gruppo-detail'),
    url(r'^circoscrizioni/$', views.CircoscrizioneListView.as_view(), name='circoscrizione-list'),
    url(r'^circoscrizioni/(?P<circoscrizione>[\w_.-]+)/$', views.CircoscrizioneDetailView.as_view(), name='circoscrizione-detail'),
    url(r'^parlamentari/$', views.ParlamentareListView.as_view(), name='parlamentare-list'),
    url(r'^parlamentari/(?P<carica>[0-9]+)/$', views.ParlamentareDetailView.as_view(), name='parlamentare-detail'),
    url(r'^sedute/$', views.SedutaListView.as_view(), name='seduta-list'),
    url(r'^sedute/(?P<seduta>[0-9]+)/$', views.SedutaDetailView.as_view(), name='seduta-detail'),
    url(r'^votazioni/$', views.VotazioneListView.as_view(), name='votazione-list'),
    url(r'^votazioni/(?P<votazione>[0-9]+)/$', views.VotazioneDetailView.as_view(), name='votazione-detail'),
)

urlpatterns = patterns('',
                       url(r'^$', views.LegislaturaListView.as_view(), name='legislatura-list'),
                       url(r'^legislatura-(?P<legislatura>[IVX0-9]+)/$', views.LegislaturaDetailView.as_view(), name='legislatura-detail'),
                       url(r'^legislatura-(?P<legislatura>[IVX0-9]+)/', include(patterns('', *urls)))
                       )


