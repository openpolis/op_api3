from django.utils.datastructures import SortedDict
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

__author__ = 'guglielmo'

class ApiRootView(APIView):
    """
    This is the main access point to the set of API at Openpolis

    * **politici** - italian politicians and their charges (from `http://politici.openpolis.it`)
    * **parlamento** - italian parliament acts and votations (16th and 17th legislature)
    * **territori** - an old, simpler version of the locations API (deprecated)

    """
    def get(self, request, **kwargs):
        format = kwargs.get('format', None)
        data = SortedDict([
            ('politici', reverse('politici:api-root', request=request, format=format)),
            ('parlamento', reverse('parlamento:legislatura-list', request=request, format=format)),
#            ('pops', reverse('pops:api-root', request=request, format=format)),
#            ('maps', reverse('maps:api-root', request=request, format=format)),
            ('territori', reverse('territori:api-root', request=request, format=format)),
        ])
        return Response(data)

