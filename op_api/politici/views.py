from django.conf import settings
from django.views.generic.list import MultipleObjectMixin
from rest_framework import generics, pagination
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from op_api.politici.models import OpUser, OpPolitician
from op_api.politici.serializers import UserSerializer, PoliticianSerializer


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'users': reverse('politici-user-list', request=request, format=format),
        'politicians': reverse('politici-politician-list', request=request, format=format),
    })

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
