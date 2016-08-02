from django.db.models import Q
from rest_framework import serializers
from parlamento.utils import get_legislatura_from_request, reverse_url, get_last_update


__author__ = 'daniele'


class LegislaturaField(serializers.Field):
    """
    Field that returns a legislature.
    """
    page_field = 'legislative_session'

    def to_native(self, value):
        request = self.context.get('request')
        return get_legislatura_from_request(request)


class UltimoAggiornamentoField(serializers.Field):
    """
    Field that returns a last update date of OpPoliticianHistoryCache.
    """
    page_field = 'update_date'

    def to_native(self, value):
        if 'data' in self.context['request'].QUERY_PARAMS:
            return self.context['request'].QUERY_PARAMS.get('date')

        return get_last_update(value.object_list.db)


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
        return value.name


class UnicodeField(serializers.CharField):
    """
    Delegates the serialisation of the field to the __unicode__ model 
    method.
    """
    def to_native(self, value):
        return value.__unicode__()


class FirstUnicodeField(serializers.CharField):
    """
    Get the first element, and return its representation.
    Delegates the serialisation of the field to the __unicode__ model
    method.
    """
    def to_native(self, value):
        return value.all()[0].__unicode__()


class FirstParliamentarianChargeField(serializers.CharField):
    """
    Get the first charge , and return its representation.
    Delegates the serialisation of the field to the __unicode__ model
    method.
    """
    def to_native(self, value):
        ret = value.filter(
            Q(charge_type__name__iexact='deputato') |
            Q(charge_type__name__icontains='senatore')
        )

        if not ret:
            ret = value.all()

        return ret[0].__unicode__()

class SedeField(serializers.CharField):
    """
    Resolve a site name
    """

    def to_native(self, value):
        # delegates field serialisation to model
        return value.__unicode__()


class HyperlinkedParlamentariField(serializers.HyperlinkedIdentityField):
    """

    """
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-list',
        })
        self.filter = kwargs.pop('filter', None)
        self.field_name = kwargs.pop('field_name', 'pk')
        super(HyperlinkedParlamentariField, self).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(
            view_name, request, format=format,
            filters={self.filter: getattr(obj, self.field_name, None)}
        )


class HyperlinkedParlamentareCacheIdentityField(
    serializers.HyperlinkedIdentityField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-cache-detail',
        })
        super(HyperlinkedParlamentareCacheIdentityField, self).__init__(*args,
                                                                 **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(view_name, request, format=format, kwargs={
            'politician_id': obj.charge.politician_id})

class HyperlinkedParlamentareIdentityField(
    serializers.HyperlinkedIdentityField):

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-detail',
        })
        super(HyperlinkedParlamentareIdentityField, self).__init__(*args,
                                                                 **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(view_name, request, format=format, kwargs={
            'politician_id': obj.pk})


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
