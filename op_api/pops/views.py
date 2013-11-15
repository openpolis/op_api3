__author__ = 'guglielmo'
from popolo.models import Person, Organization, Membership, Post
from rest_framework import viewsets

# ViewSets define the view behavior.
class PersonViewSet(viewsets.ModelViewSet):
    model = Person


class MembershipViewSet(viewsets.ModelViewSet):
    model = Membership


class OrganizationViewSet(viewsets.ModelViewSet):
    model = Organization


class PostViewSet(viewsets.ModelViewSet):
    model = Post
