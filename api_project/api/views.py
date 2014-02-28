from django.utils.datastructures import SortedDict
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

__author__ = 'guglielmo'

class ApiRootView(APIView):
    """
    Lista di tutte le legislature
    """
    def get(self, request, **kwargs):
        format = kwargs.get('format', None)
        data = SortedDict([
            ('maps', reverse('maps:api-root', request=request, format=format)),
            ('politici', reverse('politici:api-root', request=request, format=format)),
            ('parlamento', reverse('parlamento:legislatura-list', request=request, format=format)),
            ('territori', reverse('territori:api-root', request=request, format=format)),            
        ])
        return Response(data)

