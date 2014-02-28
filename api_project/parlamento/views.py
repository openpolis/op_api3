from datetime import date
from collections import OrderedDict as odict
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.compat import parse_date
from rest_framework.filters import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import generics, filters
from parlamento import lex
from parlamento.models import Carica, Gruppo, PoliticianHistoryCache, Seduta, Votazione
from parlamento.serializers import GruppoSerializer, CustomPaginationSerializer, ParlamentareSerializer, VotazioneSerializer, SedutaSerializer, VotazioneDettagliataSerializer
from parlamento.utils import reverse_url, get_legislatura_from_request, get_last_update


__author__ = 'daniele'


class DBSelectBackend(object):

    def filter_queryset(self, request, queryset, view):
        db_alias = view.db_alias
        return queryset.using(db_alias)


class APILegislaturaMixin(object):
    """
    All views in this module extends this class
    """
    filter_backends = (DBSelectBackend, DjangoFilterBackend)

    @property
    def db_alias(self):
        legislatura = lex.get_legislatura(self.legislatura)
        if legislatura.database is None:
            raise Http404("Legislatura {0} not found".format(legislatura))
        return legislatura.database

    @property
    def legislatura(self):
        """
        APIView uses a custom Request that wraps django Request
        """
        return get_legislatura_from_request(self.request)

    def prepare_legislatura(self, legislatura, request_format):
        url_kwargs = {
            'kwargs': {'legislatura': str(legislatura.number)},
            'format': request_format,
        }
        return odict([
            ('name', legislatura.name),
            ('start_date', legislatura.start_date),
            ('end_date', legislatura.end_date),
            ('voting_date', legislatura.voting_date),
            ('url', self.get_reverse_url('legislatura-detail', **url_kwargs)),
            ('groups_url', self.get_reverse_url('gruppo-list', **url_kwargs)),
            ('districts_url', self.get_reverse_url('circoscrizione-list', **url_kwargs)),
            ('parliamentarians_url', self.get_reverse_url('parlamentare-list', **url_kwargs)),
            ('sittings_url', self.get_reverse_url('seduta-list', **url_kwargs)),
            ('votes_url', self.get_reverse_url('votazione-list', **url_kwargs)),
        ])

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
        data = []
        for legislatura in lex.get_legislature():
            data.append(self.prepare_legislatura(legislatura, request_format))
        data.reverse()
        return Response(data)


class LegislaturaDetailView(APILegislaturaMixin, APIView):
    """
    Lista di tutte le , or create a new snippet.
    """
    def get(self, request, **kwargs):
        request_format = kwargs.get('format', None)
        data = self.prepare_legislatura(lex.get_legislatura(self.legislatura), request_format)
        return Response(data)


class GruppoListView(APILegislaturaMixin, generics.ListAPIView):
    queryset = Gruppo.objects.all()
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
        for c in Carica.objects.using(self.db_alias).values('district', 'charge_type_id').filter(
            charge_type_id__in=[1, 4, 5],
            district__isnull=False,
        ).distinct():
            circoscrizione = dict(name=c['district'])
            if c['charge_type_id'] == 1:
                circoscrizione['house'] = 'camera'
            elif c['charge_type_id'] in [4, 5]:
                circoscrizione['house'] = 'senato'
            else:
                circoscrizione['house'] = 'ERROR:{}'.format(c['charge_type_id'])
            circoscrizione['parliamentarians_url'] = self.get_reverse_url('parlamentare-list',
                                                                      filters={'district': c['district']},
                                                                      format=kwargs.get('format', None))
            circoscrizioni.append(circoscrizione)

        return Response({
            'results': sorted(circoscrizioni, key=lambda c: c['house'] + c['name']),
            'count': len(circoscrizioni),
            'next': None,
            'previous': None,
        })


class CircoscrizioneDetailView(APILegislaturaMixin, APIView):
    pass


class ParlamentareListView(APILegislaturaMixin, generics.ListAPIView):
    serializer_class = ParlamentareSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = PoliticianHistoryCache.objects.filter(chi_tipo='P')\
        .select_related('charge', 'group', 'charge__politician', 'charge__charge_type')
    filter_backends = APILegislaturaMixin.filter_backends + (filters.OrderingFilter,)
    ordering = ('charge__politician__surname', 'charge__politician__name') + ParlamentareSerializer.Meta.statistic_fields

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(ParlamentareListView, self).get_queryset()

        # filtro per data
        data = self.request.QUERY_PARAMS.get('date', None)
        if data:
            data = parse_date(data)
            if data > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(
                charge__start_date__lt=data,
            ).filter(Q(charge__end_date__isnull=True) | Q(charge__start_date__gt=data))
        else:
            # extract last update date to filter history cache results
            data = get_last_update(self.db_alias)
            queryset = queryset.filter(update_date=data)

        # filtro per ramo
        ramo = self.request.QUERY_PARAMS.get('house', '').upper()
        if ramo in ('C', 'S'):
            queryset = queryset.filter(house=ramo)

        # filtro per circoscrizione
        circoscrizione = self.request.QUERY_PARAMS.get('district', None)
        if circoscrizione is not None:
            queryset = queryset.filter(charge__district=circoscrizione)

        # filtro per gruppo
        gruppo = self.request.QUERY_PARAMS.get('group', None)
        if gruppo is not None:
            queryset = queryset.filter(group=int(gruppo))

        # filtro per genere
        genere = self.request.QUERY_PARAMS.get('gender', None)
        if genere in ('M', 'F'):
            queryset = queryset.filter(charge__politician__gender=genere)

        return queryset


class ParlamentareDetailView(APILegislaturaMixin, generics.RetrieveAPIView):
    serializer_class = ParlamentareSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = PoliticianHistoryCache.objects.filter(chi_tipo='P')

    def get_object(self, queryset=None):
        # Determine the base queryset to use.
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())

        last_update = get_last_update(self.db_alias)
        queryset = queryset.select_related('carica', 'carica__gruppo', 'carica__politico').filter(data=last_update)

        obj = get_object_or_404(queryset,
                                chi_id=self.kwargs.get('carica'),
                                )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class SedutaListView(APILegislaturaMixin, generics.ListAPIView):
    queryset = Seduta.objects.prefetch_related('votes')
    model = Seduta
    serializer_class = SedutaSerializer
    filter_backends = APILegislaturaMixin.filter_backends + (filters.OrderingFilter, )
    filter_fields = ('house', 'date', 'number', 'is_imported')
    ordering = ('number', 'date')


class SedutaDetailView(APILegislaturaMixin, generics.RetrieveAPIView):
    model = Seduta
    pk_url_kwarg = 'seduta'
    serializer_class = SedutaSerializer


class VotazioneListView(APILegislaturaMixin, generics.ListAPIView):
    queryset = Votazione.objects.select_related('seduta')
    model = Votazione
    serializer_class = VotazioneSerializer
    filter_fields = ('esito', 'is_imported', 'tipologia', )

    def filter_queryset(self, *args, **kwargs):
        return super(VotazioneListView, self).filter_queryset(*args, **kwargs)

    def get_queryset(self):
        qs = super(VotazioneListView, self).get_queryset()

        seduta = self.request.QUERY_PARAMS.get('seduta', None)
        if seduta is not None:
            qs = qs.filter(seduta__pk=int(seduta))

        return qs


class VotazioneDetailView(APILegislaturaMixin, generics.RetrieveAPIView):
    queryset = Votazione.objects.prefetch_related('votazionehascarica_set')
    model = Votazione
    pk_url_kwarg = 'votazione'
    serializer_class = VotazioneDettagliataSerializer


