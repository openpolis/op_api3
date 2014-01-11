# -*- coding: utf-8 -*-
from django.utils.datastructures import SortedDict
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from places.models import Place, PlaceType, Identifier, Language, ClassificationTreeTag, ClassificationTreeNode
from places.serializers import PlaceSerializer, PlaceTypeSerializer, PlaceInlineSerializer, IdentifierSerializer, \
    LanguageSerializer, ClassificationTreeTagSerializer, \
    ClassificationTreeNodeSerializer


class MapsView(APIView):
    """
    List of available resources' endpoints for the ``politici`` section of the API
    """
    def get(self, request, **kwargs):
        format = kwargs.get('format', None)
        data = SortedDict([
            ('places', reverse('maps:place-list', request=request, format=format)),
            ('placetypes', reverse('maps:placetype-list', request=request, format=format)),
            ('classifications', reverse('maps:classification-list', request=request, format=format)),
            ('identifiers', reverse('maps:identifier-list', request=request, format=format)),
            ('languages', reverse('maps:language-list', request=request, format=format)),
        ])
        return Response(data)


class PlaceListView(generics.ListCreateAPIView):
    """
    Represents the list of places

    Accepts these filters through the following **GET**
    querystring parameters:

    * ``place_type`` - get all Places with PlaceType's slug
                       matching the value
    * ``namestartswith`` - get all Places with names starting
                           with the value (case insensitive)
    * ``namecontains`` - get all Places with names containing
                         the value (case insensitive)
    * ``external_id``  - get all Places with the external_id value
                         scheme:name:value (es: ISTAT:PROVINCE_ID:58) or
                         slug:value (istat-province-id:58)
    """
    model = Place
    queryset = Place.objects.select_related('place_type',)
    serializer_class = PlaceInlineSerializer
    paginate_by = 25
    max_paginate_by = 100

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """
        queryset = super(PlaceListView, self).get_queryset()

        # fetch all places whose PlaceType's slug matches the parameter
        place_type = self.request.QUERY_PARAMS.get('place_type', None)
        if place_type:
            queryset = queryset.filter(place_type__slug=place_type)

        # fetch all places whose name starts with the parameter
        namestartswith = self.request.QUERY_PARAMS.get('namestartswith', None)
        if namestartswith:
            queryset = queryset.filter(name__istartswith=namestartswith)

        # fetch all places whose name contains the parameter
        namecontains = self.request.QUERY_PARAMS.get('namecontains', None)
        if namecontains:
            queryset = queryset.filter(name__icontains=namecontains)

        external_id = self.request.QUERY_PARAMS.get('external_id', None)
        if external_id:
            components = external_id.split(":")
            if len(components) == 2:
                (slug, value) = components
                queryset = queryset.filter(identifiers__slug=slug,
                                           placeidentifiers__value=value)
            elif len(components) == 3:
                (scheme, name, value) = components
                queryset = queryset.filter(identifiers__scheme=scheme,
                                           identifiers__name=name,
                                           placeidentifiers__value=value)
            else:
                pass

        return queryset


class PlaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that represents a single politician.
    """
    model = Place
    serializer_class = PlaceSerializer


class PlaceTypeListView(generics.ListCreateAPIView):
    """
    Represents the list of place types
    """
    model = PlaceType
    serializer_class = PlaceTypeSerializer


class PlaceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Represents a single PlaceType
    """
    model = PlaceType
    serializer_class = PlaceTypeSerializer

class IdentifierListView(generics.ListCreateAPIView):
    """
    Represents the list of external identifiers definitions
    """
    model = Identifier
    serializer_class = IdentifierSerializer


class IdentifierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Represents a single external identifier
    """
    model = Identifier
    serializer_class = IdentifierSerializer


class LanguageListView(generics.ListCreateAPIView):
    """
    Represents the list of languages
    """
    model = Language
    serializer_class = LanguageSerializer


class LanguageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Represents a single language
    """
    model = Language
    serializer_class = LanguageSerializer
    lookup_field = 'iso639_1_code'


class ClassificationListView(generics.ListCreateAPIView):
    """
    Represents the list of classifications
    """
    model = ClassificationTreeTag
    serializer_class = ClassificationTreeTagSerializer


class ClassificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Represents the detail of a classification
    """
    model = ClassificationTreeTag
    serializer_class = ClassificationTreeTagSerializer

class ClassificationNodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = ClassificationTreeNode
    serializer_class = ClassificationTreeNodeSerializer

    def get_object(self, queryset=None):
        # Perform the custom object lookup
        # using both slugs passed in self.kwargs
        # takes into consideration equivalent_to relations
        pl = Place.objects.get(slug=self.kwargs['place__slug'])
        nodes = pl.referencing_nodes(self.kwargs['tag__slug'])
        if nodes.count() == 1:
            obj = nodes[0]
        elif nodes.count() == 0:
            raise Exception("no node found for {place__slug}, {tag__slug}".format(
                **self.kwargs
            ))
        else:
            raise Exception("mode than one node found for {place__slug}, {tag__slug}".format(
                **self.kwargs
            ))

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

