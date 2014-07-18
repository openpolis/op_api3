from rest_framework.permissions import IsAuthenticatedOrReadOnly
from pops.serializers import PersonSerializer

__author__ = 'guglielmo'
from popolo.models import Person, Organization, Membership, Post, Identifier
from rest_framework import viewsets

# ViewSets define the view behavior.
class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PersonSerializer

class MembershipViewSet(viewsets.ModelViewSet):
    model = Membership
    permission_classes = (IsAuthenticatedOrReadOnly,)


class OrganizationViewSet(viewsets.ModelViewSet):
    model = Organization
    permission_classes = (IsAuthenticatedOrReadOnly,)


class PostViewSet(viewsets.ModelViewSet):
    model = Post
    permission_classes = (IsAuthenticatedOrReadOnly,)
