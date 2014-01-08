from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from api.mixins import ShortListModelMixin
from pops_old.models import Person
from pops_old.serializers import PersonSerializer


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'users': reverse('person-list', request=request),
        })


class PersonList(ShortListModelMixin, generics.ListCreateAPIView):
    """
    API endpoint that represents a list of users for the politici application.
    """
    model = Person
    serializer_class = PersonSerializer
    list_fields = ('url', 'first_name', 'last_name', 'birth_date',)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, list_fields=self.list_fields, **kwargs)


class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that represents a single user.
    """
    model = Person
    serializer_class = PersonSerializer

