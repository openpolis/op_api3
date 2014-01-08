from rest_framework import serializers

from politici.models import OpUser, OpPolitician, OpContent, OpInstitutionCharge, OpOpenContent


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpUser
        view_name = 'politici:user-detail'
        fields = ('url', 'first_name', 'last_name', 'nickname', 'is_active', 'email')


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpContent
        fields = ('id', 'created_at', 'updated_at' )

class PoliticianSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    class Meta:
        model = OpPolitician
        view_name = 'politici:politician-detail'
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location',
            'last_charge_update',
            'content',
        )


class OpenContentSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    class Meta:
        model = OpOpenContent
        #fields = ('id', 'created_at', 'updated_at' )


class OpInstitutionChargeSerializer(serializers.ModelSerializer):
    content = OpenContentSerializer()
    politician = serializers.HyperlinkedRelatedField(view_name='politici:politician-detail')
    institution = serializers.HyperlinkedRelatedField(view_name='politici:institution-detail')
    charge_type = serializers.HyperlinkedRelatedField(view_name='politici:chargetype-detail')
    location = serializers.HyperlinkedRelatedField(view_name='territori:location-detail')
    class Meta:
        model = OpInstitutionCharge
        view_name = 'politici:instcharge-detail'
        fields = (
            'politician', 'institution', 'charge_type', 'location',
            'date_start', 'date_end', 'description', 'content'
        )
