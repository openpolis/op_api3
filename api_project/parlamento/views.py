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
from parlamento.models import Carica, Gruppo, PoliticianHistoryCache, Seduta, Votazione, Sede, \
    Politico
from parlamento.serializers import CaricaSerializer, GruppoSerializer, CustomPaginationSerializer, ParlamentareCacheSerializer, \
       ParlamentareInlineSerializer, VotazioneSerializer, SedutaSerializer, VotazioneDettagliataSerializer, SedeSerializer, \
    PoliticoSerializer, CaricaInlineSerializer, \
    ParlamentareCacheInlineSerializer
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
            ('sites_url', self.get_reverse_url('sede-list', **url_kwargs)),
            ('parliamentarians_url', self.get_reverse_url('parlamentare-list', **url_kwargs)),
#            ('charges_url', self.get_reverse_url('carica-list', **url_kwargs)),
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


class SedeListView(APILegislaturaMixin, generics.ListAPIView):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer


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


class ParlamentareCacheListView(APILegislaturaMixin, generics.ListAPIView):
    """
    Represents a list of parliamentarians

    Accepts these filters through the following **GET** querystring parameters:

    * ``house``      - C for Camera, S for Senato
    * ``district``   - Name of the district (electoral councail)
                       see: http://api3.openpolis.it/parlamento/17/districts/
    * ``group``      - id of the group
                       see: http://api3.openpolis.it/parlamento/17/groups/
    * ``site``       - id of the site (commission, or other organ)
                       see: http://api3.openpolis.it/parlamento/17/sites/
    * ``gender``     - M for Male, F for Femalw

    Results are filtered by surname, name of the parliamentarian.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter

    Example usage (extract all members of the
        Commissione permanente I Affari Costituzionali at il Senato)

        >> r = requests.get('http://api3.openpolis.it/parlamento/17/parliamentarians/?site=1&format=json')
        >> res = r.json()
        >> print res['count']
        59
    """
    serializer_class = ParlamentareCacheInlineSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = PoliticianHistoryCache.objects.filter(chi_tipo='P')\
        .select_related('charge', 'group', 'charge__politician', 'charge__charge_type')\
        .prefetch_related('charge__innercharges__site')
    filter_backends = APILegislaturaMixin.filter_backends + (filters.OrderingFilter,)
    ordering = ('charge__politician__surname', 'charge__politician__name') + ParlamentareCacheSerializer.Meta.statistic_fields

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(ParlamentareCacheListView, self).get_queryset()

        # the last update from the index is taken
        last_update = get_last_update(self.db_alias)
        queryset = queryset.filter(update_date=last_update)

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

        # filtro per sede
        sede = self.request.QUERY_PARAMS.get('site', None)
        if sede is not None:
            queryset = queryset.filter(charge__innercharges__site=int(sede))

        # filtro per genere
        genere = self.request.QUERY_PARAMS.get('gender', None)
        if genere in ('M', 'F'):
            queryset = queryset.filter(charge__politician__gender=genere)

        return queryset


class ParlamentareCacheDetailView(APILegislaturaMixin,
                                  generics.RetrieveAPIView):
    serializer_class = ParlamentareCacheSerializer
    queryset = PoliticianHistoryCache.objects.filter(chi_tipo='P')

    def get_object(self, queryset=None):
        # Determine the base queryset to use.
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())

        last_update = get_last_update(self.db_alias)
        queryset = queryset.select_related('charge', 'group', 'charge__politician', 'charge__charge_type')\
            .filter(update_date=last_update)

        obj = get_object_or_404(
            queryset,
            charge__politician__id=self.kwargs.get('politician_id')
        )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ParlamentareListView(APILegislaturaMixin, generics.ListAPIView):
    """
    Represents a list of parliamentarians

    Accepts these filters through the following **GET** querystring parameters:

    * ``house``      - C for Camera, S for Senato
    * ``district``   - Name of the district (electoral councail)
                       see: http://api3.openpolis.it/parlamento/17/districts
    * ``group``      - id of the group
                       see: http://api3.openpolis.it/parlamento/17/groups
    * ``site``       - id of the site (commission, or other organ)
                       see: http://api3.openpolis.it/parlamento/17/sites
    * ``gender``     - M for Male, F for Female
    * ``status``     - A for Active, I for Inactive
                       only currently active or inactive MPs are listed
    * ``info_mode``  - C for Current, H for Historical
                       related_info shown are current or historical


    Results are ordered by surname, name of the parliamentarian.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter

    Example usage (extract all members of the
        Commissione permanente I Affari Costituzionali at il Senato)

        >> r = requests.get('http://api3.openpolis.it/parlamento/17/parliamentarians/?site=1&format=json')
        >> res = r.json()
        >> print res['count']
        59
    """
    serializer_class = ParlamentareInlineSerializer
    pagination_serializer_class = CustomPaginationSerializer
    queryset = Politico.objects\
        .select_related('charge', 'charge__charge_type')
    filter_backends = APILegislaturaMixin.filter_backends + (filters.OrderingFilter,)
    ordering = ('surname', 'name')

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """
        queryset = super(ParlamentareListView, self).get_queryset()

        # filtro per ramo
        ramo = self.request.QUERY_PARAMS.get('house', '').upper()
        if ramo == 'C':
            queryset = queryset.filter(
                charges__charge_type__name__iexact='deputato')
        if ramo == 'S':
            queryset = queryset.filter(
                charges__charge_type__name__icontains='senatore')

        # filtro per status
        # only politicians who are currently active in the parliament
        # are filtered
        status = self.request.QUERY_PARAMS.get('status', '').upper()
        if status == 'A':
            queryset = queryset.filter(
                (Q(charges__charge_type__name__iexact='deputato') |
                 Q(charges__charge_type__name__icontains='senatore')) &
                Q(charges__end_date__isnull=True)
            )
        if status == 'I':
            queryset = queryset.filter(
                (Q(charges__charge_type__name__iexact='deputato') |
                 Q(charges__charge_type__name__icontains='senatore')) &
                Q(charges__end_date__isnull=False)
            )

        # filtro per circoscrizione
        circoscrizione = self.request.QUERY_PARAMS.get('district', None)
        if circoscrizione is not None:
            queryset = queryset.filter(charges__district=circoscrizione)

        # filtro per genere
        genere = self.request.QUERY_PARAMS.get('gender', None)
        if genere in ('M', 'F'):
            queryset = queryset.filter(gender=genere)

        # filtro per info_mode
        # defines which groups and sites info are shown
        # if both (default), current or historical
        info_mode = self.request.QUERY_PARAMS.get('info_mode', None)

        # filtro per gruppo
        gruppo = self.request.QUERY_PARAMS.get('group', None)
        if gruppo is not None:
            queryset = queryset.filter(
                charges__caricahasgruppo__group_id=int(gruppo)
            )

            # current or historical info_mode add-on
            if info_mode == 'C':
                queryset = queryset.filter(
                    charges__caricahasgruppo__end_date__isnull=True
                )
            if info_mode == 'H':
                queryset = queryset.filter(
                    charges__caricahasgruppo__end_date__isnull=False
                )


        # filtro per sede
        sede = self.request.QUERY_PARAMS.get('site', None)
        if sede is not None:
            queryset = queryset.filter(charges__innercharges__site=int(sede))

            # current or historical info_mode add-on
            if info_mode == 'C':
                queryset = queryset.filter(
                    charges__innercharges__end_date__isnull=True
                )
            if info_mode == 'H':
                queryset = queryset.filter(
                    charges__innercharges__end_date__isnull=False
                )

        return queryset

class ParlamentareDetailView(APILegislaturaMixin, generics.RetrieveAPIView):
    """
    Details for a single **Parliamentarian**, include a small anagraphical
    section with:

    - `id` - the main ID, that connects openparlamento and openpolis
    - `name', `surname`, `gender` - the only anagraphical information we have in openparlamento
    - `monitoring_users` - the number of users who are monitoring this
    politician in openparlamento

    Then a list of `charges`, past or present.

    For each charge:

    - the list of past and present `groups` memberships and relevant charges,
    - the list of past and present *internal* charges
      (commitees and other internal house organs)
    """

    def get(self, request, **kwargs):
        """
        The view for a Politico is a complex beast. We go manual here.

        The get method is overriden and the db selection filter (using)
        must be explicitly called, as the usual filter_backends in the
        mixin are not called at that point.

        The response is manually built, by looping on data structure that have
        already been prefetched.

        TODO: see if it's easy to include the filters, and avoid to
        explicitly build the queryset using ``using``.
        """

        # list of all indici, sorted,
        # used to get the position of the politician
        # in a global ranking
        # TODO: this could be cached into a redis key
        #       with a 120 minutes timeout
        indici = list(
            Carica.objects.using('parlamento17').filter(
                charge_type_id__in=[1, 4, 5],
                end_date__isnull=True,
                indice__isnull=False
            ).values_list('indice', flat=True).
                order_by('-indice')
        )

        # huge prefetch, to make all queries at once
        # usually it gets faster
        p = Politico.objects.using(self.db_alias).\
            prefetch_related(
                'charges__charge_type',
                'charges__caricahasgruppo_set__group',
                'charges__caricahasgruppo_set__groupcharges',
                'charges__innercharges__site',
                'charges__innercharges__charge_type'
            ).get(pk=kwargs['politician_id'])

        # will use an odict, to keep fields sorted
        res_dict = odict([
            ('id', p.id),
            ('name', p.name), ('surname', p.surname), ('gender', p.gender),
            ('monitoring_users', p.monitoring_users),
        ])

        charges = []
        for c in p.charges.all():
            c_dict = odict([])
            c_dict['name'] = c.charge
            c_dict['start_date'] = c.start_date
            c_dict['end_date'] = c.end_date
            c_dict['repr'] = c.__unicode__()

            groups = []
            for cg in c.caricahasgruppo_set.all():
                g = cg.group
                g_dict = odict([])
                g_dict['name'] = g.name
                g_dict['acronym'] = g.acronym
                g_dict['repr'] = g.__unicode__()

                g_dict['charges'] = []
                for ig in cg.groupcharges.all():
                    i_dict = odict([])
                    i_dict['name'] = ig.charge
                    i_dict['start_date'] = ig.start_date
                    i_dict['end_date'] = ig.end_date

                    g_dict['charges'].append(i_dict)

                groups.append(g_dict)

            if groups:
                c_dict['groups'] = groups


            inner_charges = []
            for ic in c.innercharges.all():
                ic_dict = odict([])
                ic_dict['name'] = ic.charge_type.name
                ic_dict['site'] = ic.site.__unicode__()
                ic_dict['start_date'] = ic.start_date
                ic_dict['end_date'] = ic.end_date
                inner_charges.append(ic_dict)
            if inner_charges:
                c_dict['inner_charges'] = inner_charges


            show_statistics = True
            try:
                sum_votations = float(c.presenze + c.assenze + c.missioni)
            except TypeError:
                show_statistics = False

            try:
                indice_pos = indici.index(c.indice) + 1
            except ValueError:
                indice_pos = None

            try:
                rebellions_perc = "{0:.2f}".format(100. * c.ribelle / c.presenze)
            except ZeroDivisionError:
                rebellions_perc = None

            if show_statistics:
                c_dict['statistics'] = odict([
                    ('presences', c.presenze),
                    ('presences_perc',
                     "{0:.2f}".format(100. * c.presenze / sum_votations) ),
                    ('absences', c.assenze),
                    ('absences_perc',
                     "{0:.2f}".format(100. * c.assenze / sum_votations) ),
                    ('missions', c.missioni),
                    ('missions_perc',
                     "{0:.2f}".format(100. * c.missioni / sum_votations) ),
                    ('rebellions', c.ribelle),
                    ('rebellions_perc', rebellions_perc),
                    ('productivity_index', c.indice),
                    ('productivity_index_pos', indice_pos)
                ])

            charges.append(c_dict)

        res_dict['charges'] = charges
        return Response(res_dict)


class CaricaListView(APILegislaturaMixin, generics.ListAPIView):
    """
    -- DEPRECATED --
    Represents the list of institution charges

    Accepts these filters through the following **GET** querystring parameters:

    * ``started_after``  - charges started after the given date
    * ``closed_after``   - charges closed after given date
    * ``status``         - active|inactive|not_specified (a|i|n)
    * ``date``           - charges **active** on the given date
    * ``charge_type_id`` - ID of the charge_type

    Dates have the format: ``YYYY-MM-DD``

    Results can be sorted by date, specifying the ``order_by=date``
    query string parameter.
    With this parameter, results are sorted by descending
    values of ``date_start``.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter,
    or add ``.json`` to the URL.

    Example usage

        >> r = requests.get('http://api.openpolis.it/politici/instcharges.json?date=1990-01-01')
        >> res = r.json()
        >> print res['count']
        1539

    """

    model = Carica
    serializer_class = CaricaInlineSerializer
    pagination_serializer_class = CustomPaginationSerializer

    def get_queryset(self):
        queryset = super(CaricaListView, self).get_queryset()

        # fetch all charges in a given status
        charge_status = self.request.QUERY_PARAMS.get(
            'status', 'n'
        ).lower()[:1]
        if charge_status == 'a':
            queryset = queryset.filter(end_date__isnull=True)
        elif charge_status == 'i':
            queryset = queryset.filter(end_date__isnull=False)

        # fetch charges started after given date
        started_after = self.request.QUERY_PARAMS.get('started_after', None)
        if started_after:
            started_after = parse_date(started_after)
            if not started_after or started_after > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(start_date__gte=started_after)

        # fetch charges closed after given date
        closed_after = self.request.QUERY_PARAMS.get('closed_after', None)
        if closed_after:
            closed_after = parse_date(closed_after)
            if not closed_after or closed_after > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(end_date__gte=closed_after)

        # fetch all charges of a given charge_type
        charge_type_id = self.request.QUERY_PARAMS.get('charge_type', None)
        if charge_type_id:
            if ',' in charge_type_id:
                queryset = queryset.filter(charge_type_id__in=charge_type_id.split(','))
            else:
                queryset = queryset.filter(charge_type_id=charge_type_id)

        # fetch all charges of a given location
        district = self.request.QUERY_PARAMS.get('district', None)
        if district:
            queryset = queryset.filter(district=district)

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-date_start')

        return queryset



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


