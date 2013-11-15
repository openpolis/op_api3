from django.utils.datastructures import SortedDict
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from op_api.politici.views import PoliticiDBSelectMixin
from op_api.territori.models import OpLocation, OpLocationType
from op_api.territori.serializers import LocationSerializer


class TerritoriView(APIView):
    """
    List of available resources' endpoints for the ``territori`` section of the API

    * ``locations`` - list of locations
    * ``locationtypes`` - list of location types, as used in the openpolis original DB
    """
    def get(self, request, **kwargs):
        format = kwargs.get('format', None)
        data = SortedDict([
            ('locations', reverse('territori:location-list', request=request, format=format)),
            ('locationtypes', reverse('territori:locationtype-list', request=request, format=format)),
        ])
        return Response(data)


class LocationList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of locations

    Accepts these filters through the following **GET** querystring parameters:

    * ``loc_type`` - type of locations to fetch

    These are the values accepted by the ``loc_type`` filter:

    * C, c, Comune, Com, comune, c, ...
    * P, p, Provincia, Prov, Pr, provincia, ...
    * R, r, Regione, regione, Reg, ...
    * N, n, Nazione, nazione, ...

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter,
    or add ``.json`` to the URL.

    """

    LOC_TYPES = {
        'C': 'comune',
        'P': 'provincia',
        'R': 'regione',
        'N': 'nazionale',
    }

    model = OpLocation
    paginate_by = 25
    max_paginate_by = 100
    serializer_class = LocationSerializer

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(LocationList, self).get_queryset()

        # filtro per location_type
        loc_type = self.request.QUERY_PARAMS.get('loc_type', '').upper()
        if loc_type:
            loc_type = loc_type[0]
        if loc_type in self.LOC_TYPES.keys():
            lt = OpLocationType.objects.using('politici').get(name__iexact=self.LOC_TYPES[loc_type])
            queryset = queryset.filter(location_type=lt)

        return queryset

class LocationDetail(PoliticiDBSelectMixin, generics.RetrieveAPIView):
    """
    Represents a single location and show all gory details stored in the DB
    """
    model = OpLocation

class LocationTypeList(PoliticiDBSelectMixin, generics.ListAPIView):
    """
    Represents the list of location types.

    May be useful for reference when integrating location data into other datasets.
    """
    model = OpLocationType
    paginate_by = 25
    max_paginate_by = 100
