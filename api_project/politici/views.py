# -*- coding: utf-8 -*-
from datetime import date
from django.conf import settings
from django.db.models import Q
from django.utils.datastructures import SortedDict

from rest_framework import generics, pagination, authentication, permissions, filters
from rest_framework.compat import parse_date
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from territori.models import OpLocation
from .models import OpUser, OpPolitician, OpInstitution, OpChargeType, OpInstitutionCharge
from .serializers import UserSerializer, PoliticianSerializer, PoliticianExportSerializer, \
        OpInstitutionChargeSerializer, PoliticianInlineSerializer


class PoliticiDBSelectMixin(object):
    """
    Defines a filter_queryset method,
    to be added before all views that extend GenericAPIView,
    in order to select correct DB source
    """
    def filter_queryset(self, queryset):
        return queryset.using('politici')


class DefaultsMixin(object):
    """Default settings for view authentication, permissions, viewsets,
    filtering and pagination"""

    # authentication_classes = (
    #    authentication.BasicAuthentication,
    #    authentication.TokenAuthentication,
    # )

    # pemission_classes = (
    #    permissions.IsAuthenticated,
    # )

    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )



class PoliticiView(APIView):
    """
    List of available resources' endpoints for the ``politici`` section of the API
    """
    def get(self, request, **kwargs):
        format = kwargs.get('format', None)
        data = SortedDict([
            ('users [protected]', reverse('politici:user-list', request=request, format=format)),
            ('politicians', reverse('politici:politician-list', request=request, format=format)),
            ('institutions', reverse('politici:institution-list', request=request, format=format)),
            ('chargetypes', reverse('politici:chargetype-list', request=request, format=format)),
            ('institution charges', reverse('politici:instcharge-list', request=request, format=format)),
        ])
        return Response(data)



class UserList(DefaultsMixin, PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents a paginated list of users of the politici application.
    """
    model = OpUser
    serializer_class = UserSerializer
    paginate_by = 25
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']

class UserDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents a single politici user.
    """
    model = OpUser
    serializer_class = UserSerializer



class PoliticiansExport(DefaultsMixin, PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of politicians, with all details, neede for export purposes.

    It should not be used as a public view, but only with internal requests,
    in order to produce json files.
    """
    model = OpPolitician
    queryset = model.objects.select_related('content')
    serializer_class = PoliticianExportSerializer
    paginate_by = 25
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(PoliticiansExport, self).get_queryset()

        # fetch all places whose name starts with the parameter
        regional_id = self.request.QUERY_PARAMS.get('regional_id', None)
        if regional_id:
            queryset = queryset.filter(
                opinstitutioncharge__content__deleted_at__isnull=True,
                opinstitutioncharge__location__regional_id=regional_id)

        provincial_id = self.request.QUERY_PARAMS.get('provincial_id', None)
        if provincial_id:
            queryset = queryset.filter(
                opinstitutioncharge__content__deleted_at__isnull=True,
                opinstitutioncharge__location__provincial_id=provincial_id)

        return queryset


class PoliticianList(DefaultsMixin, PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of politicians

    Accepts these filters through the following **GET** querystring parameters:

    * ``namestartswith`` - get all Politicians with names starting
                           with the value (case insensitive)
    * ``namecontains``   - get all Politicians with names containing
                           the value (case insensitive)

    Results can be sorted by date, specifying the ``order_by=date``
    query string parameter.
    With this parameter, results are sorted by descending
    values of ``date_start``.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter,
    or add ``.json`` to the URL.

    Example usage

        >> r = requests.get('http://api.openpolis.it/politici/politicians.json?namestartswith=giulio')
        >> res = r.json()
        >> print res['count']
        600
    """
    model = OpPolitician
    queryset = model.objects.select_related('content')
    serializer_class = PoliticianInlineSerializer
    paginate_by = 25
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(PoliticianList, self).get_queryset()

        # exclude deleted content
        # queryset = queryset.exclude(content__deleted_at__isnull=False)

        # fetch all places whose name starts with the parameter
        namestartswith = self.request.QUERY_PARAMS.get('namestartswith', None)
        if namestartswith:
            queryset = queryset.filter(
                Q(first_name__istartswith=namestartswith) |
                Q(last_name__istartswith=namestartswith)
            )

        # fetch all places whose name contains the parameter
        namecontains = self.request.QUERY_PARAMS.get('namecontains', None)
        if namecontains:
            queryset = queryset.filter(
                Q(first_name__icontains=namecontains) |
                Q(last_name__icontains=namecontains)
            )


        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-birth_date')

        return queryset


class PoliticianDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    API endpoint that represents a single politician.
    """
    model = OpPolitician
    serializer_class = PoliticianSerializer


class InstitutionList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of institutions
    """
    model = OpInstitution
    paginate_by = 25
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']

class InstitutionDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents the details of an institution
    """
    model = OpInstitution


class ChargeTypeList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of charge types
    """
    model = OpChargeType
    paginate_by = 25
    max_paginate_by = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']

class ChargeTypeDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents the details of the charge type
    """
    model = OpChargeType


class InstitutionChargeList(
    DefaultsMixin,
    PoliticiDBSelectMixin,
    generics.ListAPIView
):
    """
    Represents the list of institution charges

    Accepts these filters through the following **GET** querystring parameters:

    * ``started_after``  - charges started after the given date
    * ``closed_after``   - charges closed after given date
    * ``status``         - active|inactive|not_specified (a|i|n)
    * ``date_from``      - all charges starting exactly at the given date
    * ``date_to``        - charges that start before this date
    * ``date``           - charges **active** on the given date
    * ``institution_id`` - ID of the institution
    * ``charge_type_id`` - ID of the charge_type
    * ``location_id``    - ID of the location
    * ``updated_after``  - charges updated after given timestamp

    Dates have the format: `YYYY-MM-DD`

    Timestamps have the format: `YYYY-MM-DDTHH:MM:SSZ`


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
    model = OpInstitutionCharge
    serializer_class = OpInstitutionChargeSerializer
    queryset = model.objects. \
        prefetch_related('politician__education_levels__education_level').\
        select_related('institution', 'charge_type', 'location',
                       'politician', 'politician__profession',
                       'politician__content',
                       'politician__content__opopencontent',
                       'party', 'group',
                       'constituency', 'constituency__election_type',
                       'content', 'content__content').\
        exclude(content__deleted_at__isnull=False)


    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(InstitutionChargeList, self).get_queryset()

        # date filters
        # date format is YYYY-MM-DD

        # exclude deleted content
        queryset = queryset.exclude(content__deleted_at__isnull=False)

        # fetch all charges in a given status
        charge_status = self.request.QUERY_PARAMS.get(
            'status', 'n'
        ).lower()[:1]
        if charge_status == 'a':
            queryset = queryset.filter(date_end__isnull=True)
        elif charge_status == 'i':
            queryset = queryset.filter(date_end__isnull=False)

        # fetch charges started after given date
        started_after = self.request.QUERY_PARAMS.get('started_after', None)
        if started_after:
            started_after = parse_date(started_after)
            if not started_after or started_after > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_start__gte=started_after)

        # fetch charges closed after given date
        closed_after = self.request.QUERY_PARAMS.get('closed_after', None)
        if closed_after:
            closed_after = parse_date(closed_after)
            if not closed_after or closed_after > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_end__gte=closed_after)

        # fetch all charges started exactly on a given date
        date_from = self.request.QUERY_PARAMS.get('date_from', None)
        if date_from:
            date_from = parse_date(date_from)
            if not date_from or date_from > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_start=date_from)

        # fetch all charges ended exactly on a given date
        date_to = self.request.QUERY_PARAMS.get('date_to', None)
        if date_to:
            date_to = parse_date(date_to)
            if not date_to or date_to > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_end=date_to)

        # fetch all charges active on a given date
        data = self.request.QUERY_PARAMS.get('date', None)
        if data:
            data = parse_date(data)
            if not data or data > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(
                date_start__lt=data,
            ).filter(Q(date_end__isnull=True) | Q(date_end__gt=data))

        # fetch all charges of a given institution
        institution_id = self.request.QUERY_PARAMS.get('institution_id', None)
        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)

        # fetch all charges of a given charge_type
        charge_type_id = self.request.QUERY_PARAMS.get('charge_type_id', None)
        if charge_type_id:
            if ',' in charge_type_id:
                queryset = queryset.filter(charge_type_id__in=charge_type_id.split(','))
            else:
                queryset = queryset.filter(charge_type_id=charge_type_id)

        # fetch all charges of a given location
        location_id = self.request.QUERY_PARAMS.get('location_id', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-date_start')

        # fetch all charges updated after a given timestamp
        updated_after = self.request.QUERY_PARAMS.get(
            'updated_after', None
        )
        if updated_after:
            queryset = queryset.filter(
                content__content__updated_at__gt=updated_after
            )

        return queryset

class InstitutionChargeDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents the details of an institution charge
    """
    model = OpInstitutionCharge
    queryset = model.objects.select_related('content')
    serializer_class = OpInstitutionChargeSerializer


class HistoricalCityMayorsView(APIView):
    """
    List all top charges for a given city, during the years

    Accepts these filters through the following **GET** querystring parameters:

    * ``date_from`` - charges that end after this date
    * ``date_to`` - charges that start before this date
    * ``date`` - charges **active** on the date

    Dates have the format: ``YYYY-MM-DD``

    Results are sorted by descending ``date_start``.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter,
    or add ``.json`` to the URL.

    Example usage::

        All mayors in Rome, between 1/1/1990 and 31/12/1999
        >> r = requests.get('http://api.openpolis.it/politici/city_mayors/5132?date_from=1990-01-01&date_to=1999-12-31')
        >> res = r.json()
        >> print res['count']
        2

    """
    def get(self, request, **kwargs):
        location_id = kwargs['location_id']
        try:
            data = self.get_city_mayors_data(location_id)
        except Exception, e:
            data = { 'error': e }

        return Response(data)

    def get_location(self, city_id):
        """
        Return the Location object, given the location_id
        """
        location = OpLocation.objects.using('politici').get(id=city_id)
        if location.location_type.name.lower() != 'comune':
            raise  Exception('location is not a city. only cities are accepted')
        return location

    def get_city_mayors_data(self, city_id):
        """get all top charges for a given city during the years"""
        data = {}
        try:
            location = self.get_location(city_id)
            data['location'] = "%s (%s)" % (location.name, location.prov)
        except Exception, detail:
            return { 'exception': 'Error retrieving location with location_id: %s. %s' % (city_id, detail) }

        ics = OpInstitutionCharge.objects.db_manager('politici').exclude(content__deleted_at__isnull=False).filter(
            Q(location__id=location.id),
            Q(charge_type__name='Sindaco') | Q(charge_type__name='Commissario straordinario') |
            Q(charge_type__name='Vicesindaco facente funzione sindaco'),
        ).order_by('-date_start')

        # fetch all charges started exactly on a given date
        date_from = self.request.QUERY_PARAMS.get('date_from', None)
        if date_from:
            date_from = parse_date(date_from)
            if not date_from or date_from > date.today():
                # TODO: raise an Exception
                return {'sindaci': []}
            ics = ics.filter(Q(date_end__isnull=True) | Q(date_end__gt=date_from))

        # fetch all charges ended exactly on a given date
        date_to = self.request.QUERY_PARAMS.get('date_to', None)
        if date_to:
            date_to = parse_date(date_to)
            ics = ics.filter(date_start__lte=date_to)

        # fetch all charges active on a given date
        given_date = self.request.QUERY_PARAMS.get('date', None)
        if given_date:
            given_date = parse_date(given_date)
            if not given_date or given_date > date.today():
                # TODO: raise an Exception
                return {'sindaci': []}
            ics = ics.filter(
                date_start__lte=given_date,
            ).filter(Q(date_end__isnull=True) | Q(date_end__gte=given_date))


        data['sindaci'] = []
        for ic in ics:
            charge_id = ic.content_id
            if ic.charge_type.name == 'Sindaco':
                c = {
                    'charge_type': 'Sindaco',
                    'date_start': ic.date_start,
                    'date_end': ic.date_end,
                    'party_acronym': ic.party.getNormalizedAcronymOrName(),
                    'party_name': ic.party.getName(),
                    'first_name': ic.politician.first_name,
                    'last_name': ic.politician.last_name,
                    'birth_date': ic.politician.birth_date,
                    'picture_url': 'http://politici.openpolis.it/politician/picture?content_id=%s' % ic.politician.content_id,
                    'op_link': 'http://politici.openpolis.it/politico/%s' % ic.politician.content_id
                }
            elif (ic.charge_type.name == 'Vicesindaco facente funzione sindaco'):
                c = {
                    'charge_type': 'Vicesindaco f.f.',
                    'date_start': ic.date_start,
                    'date_end': ic.date_end,
                    'party_acronym': ic.party.getNormalizedAcronymOrName(),
                    'party_name': ic.party.getName(),
                    'first_name': ic.politician.first_name,
                    'last_name': ic.politician.last_name,
                    'birth_date': ic.politician.birth_date,
                    'picture_url': 'http://politici.openpolis.it/politician/picture?content_id=%s' % ic.politician.content_id,
                    'op_link': 'http://politici.openpolis.it/politico/%s' % ic.politician.content_id
                }
            else:
                c = {
                    'charge_type': 'Commissario',
                    'date_start': ic.date_start,
                    'date_end': ic.date_end,
                    'first_name': ic.politician.first_name,
                    'last_name': ic.politician.last_name,
                    'birth_date': ic.politician.birth_date,
                    'description': ic.description,
                    'op_link': 'http://politici.openpolis.it/politico/%s' % ic.politician.content_id
                }

            data['sindaci'].append(c)

        return data
