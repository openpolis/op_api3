from django.conf.urls import patterns, include, url
from op_api.parlamento import views

__author__ = 'daniele'


urls = (
    url(r'^gruppi/$', views.GruppoListView.as_view(), name='gruppo-list'),
    url(r'^gruppi/(?P<gruppo>[\w_.-]+)/$', views.GruppoDetail.as_view(), name='gruppo-detail'),
    url(r'^circoscrizioni/$', views.CircoscrizioneListView.as_view(), name='circoscrizione-list'),
    url(r'^circoscrizioni/(?P<circoscrizione>[\w_.-]+)/$', views.CircoscrizioneDetailView.as_view(), name='circoscrizione-detail'),
    url(r'^parlamentari/$', views.ParlamentareListView.as_view(), name='parlamentare-list'),
    url(r'^parlamentari/(?P<carica>[0-9]+)$', views.ParlamentareDetailView.as_view(), name='parlamentare-detail'),
)

urlpatterns = patterns('',
                       url(r'^$', views.LegislaturaListView.as_view(), name='legislatura-list'),
                       url(r'^legislatura-(?P<legislatura>[IVX]+)/$', views.LegislaturaDetailView.as_view(), name='legislatura-detail'),
                       url(r'^legislatura-(?P<legislatura>[IVX]+)/', include(patterns('', *urls)))
                       )


