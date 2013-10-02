from rest_framework import serializers
from op_api.parlamento.utils import get_legislatura_from_request, reverse_url, get_last_update


__author__ = 'daniele'


class LegislaturaField(serializers.Field):
    """
    Field that returns a legislature.
    """
    page_field = 'legislatura'

    def to_native(self, value):
        request = self.context.get('request')
        return get_legislatura_from_request(request)


class UltimoAggiornamentoField(serializers.Field):
    """
    Field that returns a last update date of OpPoliticianHistoryCache.
    """
    page_field = 'data'

    def to_native(self, value):
        if 'data' in self.context['request'].QUERY_PARAMS:
            return self.context['request'].QUERY_PARAMS.get('data')
        return get_last_update()


class RamoField(serializers.CharField):
    """
    Field that returns a verbose name of ramo.
    """

    def to_native(self, value):
        return {
            'S': 'Senato',
            'C': 'Camera'
        }[value.upper()]


class CaricaField(serializers.CharField):
    """
    Resolve a charge name
    """

    def to_native(self, value):
        return value.nome


class HyperlinkedParlamentariField(serializers.HyperlinkedIdentityField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-list',
        })
        self.filter = kwargs.pop('filter', None)
        super(HyperlinkedParlamentariField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(
            view_name, request, format=format, filters={self.filter: obj.pk}
        )


class HyperlinkedParlamentareField(serializers.HyperlinkedRelatedField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-detail',
        })
        super(HyperlinkedParlamentareField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(view_name, request, format=format, kwargs={'carica': obj.pk})


class HyperlinkedSedutaField(serializers.HyperlinkedRelatedField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'seduta-detail',
        })
        super(HyperlinkedSedutaField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, request_format):
        return reverse_url(
            view_name, request, format=request_format, kwargs={'seduta': obj.pk}
        )


class HyperlinkedVotazioneField(serializers.HyperlinkedRelatedField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'votazione-detail',
        })
        super(HyperlinkedVotazioneField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, request_format):
        return reverse_url(
            view_name, request, format=request_format, kwargs={'votazione': obj.pk}
        )


class HyperlinkedVotazioneIdentityField(serializers.HyperlinkedIdentityField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'votazione-detail',
        })
        super(HyperlinkedVotazioneIdentityField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, request_format):
        return reverse_url(
            view_name, request, format=request_format, kwargs={'votazione': obj.pk}
        )
