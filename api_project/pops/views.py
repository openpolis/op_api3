from rest_framework.permissions import IsAuthenticatedOrReadOnly
from pops.serializers import PersonSerializer, OrganizationSerializer, PostSerializer, MembershipSerializer, \
    OrganizationInlineSerializer, PostInlineSerializer, PersonInlineSerializer

__author__ = 'guglielmo'
from popolo.models import Person, Organization, Membership, Post, Identifier
from rest_framework import viewsets

# ViewSets define the view behavior.
class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PersonInlineSerializer
        return PersonSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    model = Organization
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationInlineSerializer
        return OrganizationSerializer


class PostViewSet(viewsets.ModelViewSet):
    model = Post
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return PostInlineSerializer
        return PostSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    model = Membership
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MembershipSerializer

