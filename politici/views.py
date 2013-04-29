from django.views.generic.list import MultipleObjectMixin

from op_api3.mixins import ShortListModelMixin
from politici.models import OpUser
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from politici.serializers import UserSerializer

@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'users': reverse('opuser-list', request=request),
        })

class PoliticiDBSelectMixin(MultipleObjectMixin):
    def get_queryset(self):
        queryset = super(PoliticiDBSelectMixin, self).get_queryset()
        return queryset.using('politici')




class UserList(PoliticiDBSelectMixin, ShortListModelMixin, generics.ListCreateAPIView):
    """
    API endpoint that represents a list of users for the politici application.
    """
    model = OpUser
    serializer_class = UserSerializer
    list_fields = ('url', 'nickname')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, list_fields=self.list_fields, **kwargs)


class UserDetail(PoliticiDBSelectMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that represents a single user.
    """
    model = OpUser
    serializer_class = UserSerializer

