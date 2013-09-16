from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import generics, pagination, filters
from op_api.parlamento.fields import LegislaturaField, UltimoAggiornamentoField
from op_api.parlamento.models import Carica, Gruppo, PoliticianHistoryCache
from op_api.parlamento.serializers import GruppoSerializer, ParlamentareSerializer
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
        }
        return Response(data)


class GruppoListView(generics.ListAPIView, APILegislaturaMixin):
    queryset = Gruppo.objects.using('politici').all()
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
        for c in Carica.objects.using('politici').values('circoscrizione', 'tipo_carica_id').filter(
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

        return Response(circoscrizioni)


class CircoscrizioneDetailView(APILegislaturaMixin, APIView):
    pass


class CustomPaginationSerializer(pagination.PaginationSerializer):

    legislatura = LegislaturaField(source='*')
    data = UltimoAggiornamentoField(source='*')


class ParlamentareListView(generics.ListAPIView, APILegislaturaMixin):
    serializer_class = ParlamentareSerializer
    pagination_serializer_class = CustomPaginationSerializer
    #queryset = Carica.objects.using('politici').filter(tipo_carica_id__in=[1, 4, 5])
    queryset = PoliticianHistoryCache.objects.using('politici').filter(chi_tipo='P')
    filter_backends = (filters.OrderingFilter,)
    ordering = ParlamentareSerializer.Meta.statistic_fields

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(ParlamentareListView, self).get_queryset()

        # extract last update date to filter history cache results
        last_update = get_last_update(queryset)
        queryset = queryset.select_related('carica', 'carica__gruppo', 'carica__politico').filter(data=last_update)

        # filtro per ramo
        ramo = self.request.QUERY_PARAMS.get('ramo', None)
        if ramo == 'camera':
            queryset = queryset.filter(ramo='C')
        elif ramo == 'senato':
            queryset = queryset.filter(ramo='S')

        # filtro per circoscrizione
        circoscrizione = self.request.QUERY_PARAMS.get('circoscrizione', None)
        if circoscrizione is not None:
            queryset = queryset.filter(carica__circoscrizione=circoscrizione)

        # filtro per gruppo
        gruppo = self.request.QUERY_PARAMS.get('gruppo', None)
        if gruppo is not None:
            queryset = queryset.filter(gruppo=int(gruppo))

        return queryset


class ParlamentareDetailView(APILegislaturaMixin, APIView):
    pass
