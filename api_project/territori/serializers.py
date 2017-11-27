from rest_framework import serializers
from territori.models import OpLocation

__author__ = 'guglielmo'
class LocationSerializer(serializers.ModelSerializer):
    """
    """
    id = serializers.HyperlinkedIdentityField(view_name='territori:location-detail')
    class Meta:
        model = OpLocation
        fields = (
            'id', 'location_type', 'name', 'inhabitants',
            'macroregional_id', 'regional_id', 'provincial_id', 'city_id',
            'prov'
        )
