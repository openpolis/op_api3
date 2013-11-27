from urllib import urlencode

from django.db.models import Max
from rest_framework.reverse import reverse

from op_api.parlamento.models import PoliticianHistoryCache


__author__ = 'daniele'


def get_legislatura_from_request(request):
    """
    Extract kwarg "legislatura" from request matched url
    """
    return request.resolver_match.kwargs.get('legislatura', None)


def get_last_update(db_alias):
    return PoliticianHistoryCache.objects.using(db_alias).aggregate(
        last_update=Max('update_date')
    )['last_update']


def reverse_url(name, request, format=None, legislatura=None, args=None, kwargs=None, filters=None):
    """
    This method helps to build a url for a specific Legislatura
    """
    if not args: args = []
    if not kwargs: kwargs = {}
    if not filters: filters = {}

    _kwargs = kwargs.copy()
    if not 'legislatura' in _kwargs:
        _kwargs.update({'legislatura': legislatura or get_legislatura_from_request(request), })

    url = reverse(
        'parlamento:{0}'.format(name),
        args=args,
        kwargs=_kwargs,
        request=request,
        format=format
    )
    return url if not filters else "{0}?{1}".format(url, urlencode(filters))
