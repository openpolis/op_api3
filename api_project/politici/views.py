# -*- coding: utf-8 -*-
from datetime import date
from django.db.models import Q
from django.utils.datastructures import SortedDict

from rest_framework import generics, pagination
from rest_framework.compat import parse_date
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from politici.models import OpUser, OpPolitician, OpInstitution, OpChargeType, OpInstitutionCharge
from politici.serializers import UserSerializer, PoliticianSerializer, OpInstitutionChargeSerializer
from territori.models import OpLocation


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


class PoliticiDBSelectMixin(object):
    """
    Defines a filter_queryset method,
    to be added before all views that extend GenericAPIView,
    in order to select correct DB source
    """
    def filter_queryset(self, queryset):
        return queryset.using('politici')


class UserList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents a paginated list of users of the politici application.
    """
    permission_classes = (IsAuthenticated,)
    model = OpUser
    serializer_class = UserSerializer
    paginate_by = 25
    max_paginate_by = 100

class UserDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents a single politici user.
    """
    permission_classes = (IsAuthenticated,) 
    model = OpUser
    serializer_class = UserSerializer


class PoliticianList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of politicians
    """
    model = OpPolitician
    queryset = model.objects.select_related('content')
    serializer_class = PoliticianSerializer
    paginate_by = 25
    max_paginate_by = 100

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
    max_paginate_by = 100

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
    max_paginate_by = 100

class ChargeTypeDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents the details of the charge type
    """
    model = OpChargeType


class InstitutionChargeList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of institution charges

    Accepts these filters through the following **GET** querystring parameters:

    * ``date_start`` - charges started *exactly* on the date
    * ``date_end`` - charges ended *exactly* on the date
    * ``date`` - charges **active** on the date
    * ``institution_id`` - ID of the institution
    * ``charge_type_id`` - ID of the charge_type
    * ``location_id`` - ID of the location

    Dates have the format: ``YYYY-MM-DD``

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
    queryset = model.objects.select_related('content')
    serializer_class = OpInstitutionChargeSerializer
    paginate_by = 25
    max_paginate_by = 100

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(InstitutionChargeList, self).get_queryset()

        # date filters
        # date format is YYYY-MM-DD

        # fetch all charges started exactly on a given date
        date_start = self.request.QUERY_PARAMS.get('date_start', None)
        if date_start:
            date_start = parse_date(date_start)
            if not date_start or date_start > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_start=date_start)

        # fetch all charges ended exactly on a given date
        date_end = self.request.QUERY_PARAMS.get('date_end', None)
        if date_end:
            date_end = parse_date(date_end)
            if not date_end or date_end > date.today():
                # TODO: raise an Exception
                return queryset.none()

            queryset = queryset.filter(date_end=date_end)

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
            queryset = queryset.filter(charge_type_id=charge_type_id)

        # fetch all charges of a given location
        location_id = self.request.QUERY_PARAMS.get('location_id', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)

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

        ics = OpInstitutionCharge.objects.db_manager('politici').filter(
            Q(location__id=location.id),
            Q(charge_type__name='Sindaco') | Q(charge_type__name='Commissario straordinario'),
        ).order_by('-date_start')

        data['sindaci'] = []
        for ic in ics:
            charge_id = ic.content_id
            if ic.charge_type.name == 'Sindaco':
                c = {
                    'charge_type': 'Sindaco',
                    'date_start': ic.date_start,
                    'date_end': ic.date_end,
                    'party': ic.party.getNormalizedAcronymOrName(),
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
                    'motivazione': ic.description,
                    'op_link': 'http://politici.openpolis.it/politico/%s' % ic.politician.content_id
                }

            data['sindaci'].append(c)

        return data
