from django.db.models import Q
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from pops.serializers import PersonSerializer, OrganizationSerializer, PostSerializer, MembershipSerializer, \
    OrganizationInlineSerializer, PostInlineSerializer, MembershipInlineSerializer, AreaSerializer

__author__ = 'guglielmo'
from popolo.models import Person, Organization, Membership, Post, Identifier, Area
from rest_framework import viewsets

# ViewSets define the view behavior.
class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        return PersonSerializer

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(PersonViewSet, self).get_queryset()

        # fetch all persons with memberships in the given area
        area_id = self.request.QUERY_PARAMS.get('area_id', None)
        if area_id:
            queryset = queryset.filter(
                memberships__area_id=area_id
            )

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-birth_date')

        return queryset


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Represents the list of organizations

    Accepts these filters through the following **GET** querystring parameters:

    * ``namestartswith`` - get all Organizations with names starting
                           with the value (case insensitive)
    * ``area_id`` - get all Organizations having area_id

    Results can be sorted by date, specifying the ``order_by=date``
    query string parameter.
    With this parameter, results are sorted by descending
    values of ``date_start``.

    Results have a standard pagination, with 25 results per page.

    To get JSON format, specify ``format=json`` as a **GET** parameter.

    Example usage

        >> r = requests.get('http://api.openpolis.it/pops/organizations.json?namestartswith=giunta')
        >> res = r.json()
        >> print res['count']
       1
    """
    model = Organization
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(OrganizationViewSet, self).get_queryset()

        # fetch all organizations whose name starts with the parameter
        namestartswith = self.request.QUERY_PARAMS.get('namestartswith', None)
        if namestartswith:
            queryset = queryset.filter(
                name__istartswith=namestartswith
            )

        # fetch all organizations for a given area
        area_id = self.request.QUERY_PARAMS.get('area_id', None)
        if area_id:
            queryset = queryset.filter(
                area__id=area_id
            )

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-start_date')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationInlineSerializer
        return OrganizationSerializer


class PostViewSet(viewsets.ModelViewSet):
    model = Post
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(PostViewSet, self).get_queryset()

        # fetch all posts for a given area
        area_id = self.request.QUERY_PARAMS.get('area_id', None)
        if area_id:
            queryset = queryset.filter(
                area__id=area_id
            )

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-start_date')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PostInlineSerializer
        return PostSerializer



class MembershipViewSet(viewsets.ModelViewSet):
    model = Membership
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Add filters to queryset provided in url querystring.
        """

        queryset = super(MembershipViewSet, self).get_queryset()

        # fetch all memberships for a given area
        area_id = self.request.QUERY_PARAMS.get('area_id', None)
        if area_id:
            queryset = queryset.filter(
                area__id=area_id
            )

        order_by = self.request.QUERY_PARAMS.get('order_by', None)
        if order_by:
            if order_by == 'date':
                queryset = queryset.order_by('-start_date')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return MembershipInlineSerializer
        return MembershipSerializer


class AreaViewSet(viewsets.ModelViewSet):
    model = Area
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        return AreaSerializer
