from rest_framework.permissions import IsAuthenticatedOrReadOnly

__author__ = 'guglielmo'
from popolo.models import Person, Organization, Membership, Post
from rest_framework import viewsets

# ViewSets define the view behavior.
class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    permission_classes = (IsAuthenticatedOrReadOnly,)


class MembershipViewSet(viewsets.ModelViewSet):
    model = Membership
    permission_classes = (IsAuthenticatedOrReadOnly,)


class OrganizationViewSet(viewsets.ModelViewSet):
    model = Organization
    permission_classes = (IsAuthenticatedOrReadOnly,)


class PostViewSet(viewsets.ModelViewSet):
    model = Post
    permission_classes = (IsAuthenticatedOrReadOnly,)
