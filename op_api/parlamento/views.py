from datetime import date
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.compat import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import generics, filters
from op_api.parlamento.models import Carica, Gruppo, PoliticianHistoryCache, Seduta, Votazione
from op_api.parlamento.serializers import GruppoSerializer, CustomPaginationSerializer, ParlamentareSerializer, VotazioneSerializer, SedutaSerializer, VotazioneDettagliataSerializer
from op_api.parlamento.utils import reverse_url, get_legislatura_from_request, get_last_update


__author__ = 'daniele'


class APILegislaturaMixin(object):
    """
    All views in this module extends this class
    """

    @property
    def legislatura(self):
        """
        APIView uses a custom Request that wraps django Request
        """
        return get_legislatura_from_request(self.request)

    def get_reverse_url(self, name, format=None, legislatura=None, args=None, kwargs=None, filters=None):

        return reverse_url(
            name,
            self.request,
            format=format,
            legislatura=legislatura or self.legislatura,
            args=args,
            kwargs=kwargs,
            filters=filters)


class LegislaturaListView(APILegislaturaMixin, APIView):
    """
    Lista di tutte le legislature
    """
    def get(self, request, **kwargs):
        request_format = kwargs.get('format', None)
        data = {
            'XVI': self.get_reverse_url('legislatura-detail', kwargs={'legislatura': 'XVI'}, format=request_format),
            'XVII': self.get_reverse_url('legislatura-detail', kwargs={'legislatura': 'XVII'}, format=request_format),
        }
        return Response(data)


class LegislaturaDetailView(APILegislaturaMixin, APIView):
    """
    Lista di tutte le , or create a new snippet.
    """
    def get(self, request, **kwargs):
        request_format = kwargs.get('format', None)
        data = {
            'gruppi': self.get_reverse_url('gruppo-list', format=request_format),
            'circoscrizioni': self.get_reverse_url('circoscrizione-list', format=request_format),
            'parlamentari': self.get_reverse_url('parlamentare-list', format=request_format),
            'sedute': self.get_reverse_url('seduta-list', format=request_format),
            'votazioni': self.get_reverse_url('votazione-list', format=request_format),
        }
        return Response(data)


class GruppoListView(generics.ListAPIView, APILegislaturaMixin):
    queryset = Gruppo.objects.using('parlamento17').all()
    serializer_class = GruppoSerializer


class GruppoDetail(APILegislaturaMixin, APIView):
    pass


class CircoscrizioneListView(APILegislaturaMixin, APIView):
    """
    Computa la lista delle circoscrizioni,
    filtrabili per ramo del parlamento.
    """
    def get(self, request, *args, **kwargs):
        circoscrizioni = []
        for c in Carica.objects.using('parlamento17').values('circoscrizione', 'tipo_carica_id').filter(
            tipo_carica_id__in=[1, 4, 5],
            circoscrizione__isnull=False,
        ).distinct():
            circoscrizione = dict(nome=c['circoscrizione'])
            if c['tipo_carica_id'] == 1:
                circoscrizione['ramo'] = 'camera'
            elif c['tipo_carica_id'] in [4, 5]:
                circoscrizione['ramo'] = 'senato'
            else:
                circoscrizione['ramo'] = 'ERROR:{}'.format(c['tipo_carica_id'])
            circoscrizione['parlamentari_url'] = self.get_reverse_url('parlamentare-list',
                                                                      filters={'circoscrizione': c['circoscrizione']},
                                                                      format=kwargs.get('format', None))
            circoscrizioni.append(circoscrizione)

        return Response({
            'results': sorted(circoscrizioni, key=lambda c: c['ramo'] + c['nome']),
            'count': len(circoscrizioni),
            'next': None,
            'previous': None,
        })


class CircoscrizioneDetailView(APILegislaturaMixin, APIView):
    pass


class ParlamentareListView(generics.ListAPIView, APILegislaturaMixin):
    serializer_class = ParlamentareSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = PoliticianHistoryCache.objects.using('parlamento17')\
        .filter(chi_tipo='P')\
        .select_related('carica', 'gruppo', 'carica__politico', 'carica__tipo_carica')
    filter_backends = (filters.OrderingFilter,)
    ordering = ('carica__politico__cognome', 'carica__politico__nome') + ParlamentareSerializer.Meta.statistic_fields

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(ParlamentareListView, self).get_queryset()

        # extract last update date to filter history cache results
        self.last_update = get_last_update()
        queryset = queryset.filter(data=self.last_update)

        # filtro per data
        data = self.request.QUERY_PARAMS.get('data', None)
        if data:
            data = parse_date(data)
            if data > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(
                carica__data_inizio__lt=data,
            ).filter(Q(carica__data_fine__isnull=True) | Q(carica__data_inizio__gt=data))

        # filtro per ramo
        ramo = self.request.QUERY_PARAMS.get('ramo', None)
        if ramo in ('C', 'S'):
            queryset = queryset.filter(ramo=ramo)

        # filtro per circoscrizione
        circoscrizione = self.request.QUERY_PARAMS.get('circoscrizione', None)
        if circoscrizione is not None:
            queryset = queryset.filter(carica__circoscrizione=circoscrizione)

        # filtro per gruppo
        gruppo = self.request.QUERY_PARAMS.get('gruppo', None)
        if gruppo is not None:
            queryset = queryset.filter(gruppo=int(gruppo))

        # filtro per genere
        genere = self.request.QUERY_PARAMS.get('genere', None)
        if genere in ('M', 'F'):
            queryset = queryset.filter(carica__politico__sesso=genere)

        return queryset


class ParlamentareDetailView(generics.RetrieveAPIView, APILegislaturaMixin):
    serializer_class = ParlamentareSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = PoliticianHistoryCache.objects.using('parlamento17').filter(chi_tipo='P')

    def get_object(self, queryset=None):
        # Determine the base queryset to use.
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())

        last_update = get_last_update()
        queryset = queryset.select_related('carica', 'carica__gruppo', 'carica__politico').filter(data=last_update)

        obj = get_object_or_404(queryset,
                                chi_id=self.kwargs.get('carica'),
                                )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class SedutaListView(generics.ListAPIView, APILegislaturaMixin):
    queryset = Seduta.objects.using('parlamento17').prefetch_related('votazione_set')
    model = Seduta
    serializer_class = SedutaSerializer
    filter_backends = (filters.OrderingFilter, filters.DjangoFilterBackend, )
    filter_fields = ('ramo', 'data', 'numero', 'is_imported')
    ordering = ('numero', 'data')


class SedutaDetailView(generics.RetrieveAPIView, APILegislaturaMixin):
    queryset = Seduta.objects.using('parlamento17')
    model = Seduta
    pk_url_kwarg = 'seduta'
    serializer_class = SedutaSerializer


class VotazioneListView(generics.ListAPIView, APILegislaturaMixin):
    queryset = Votazione.objects.using('parlamento17').select_related('seduta')
    model = Votazione
    serializer_class = VotazioneSerializer
    filter_fields = ('esito', 'is_imported', 'tipologia', )

    def get_queryset(self):
        qs = super(VotazioneListView, self).get_queryset()

        seduta = self.request.QUERY_PARAMS.get('seduta', None)
        if seduta is not None:
            qs = qs.filter(seduta__pk=int(seduta))

        return qs


class VotazioneDetailView(generics.RetrieveAPIView, APILegislaturaMixin):
    queryset = Votazione.objects.using('parlamento17').prefetch_related('votazionehascarica_set')
    model = Votazione
    pk_url_kwarg = 'votazione'
    serializer_class = VotazioneDettagliataSerializer


