from rest_framework import serializers

from politici.models import OpUser, OpResources, OpPolitician, OpContent, OpInstitutionCharge, OpOpenContent, OpParty


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpUser
        view_name = 'politici:user-detail'
        fields = ('url', 'first_name', 'last_name', 'nickname', 'is_active', 'email')


class ResourceSerializer(serializers.ModelSerializer):
    resource_type = serializers.CharField(source='resources_type_denominazione', read_only=True)
    value = serializers.CharField(source='valore', read_only=True)
    description = serializers.CharField(source='descrizione', read_only=True)
    class Meta:
        model = OpResources
        fields = ('resource_type', 'value', 'description' )

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpContent
        fields = ('id', 'created_at', 'updated_at' )



class OpenContentSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    class Meta:
        model = OpOpenContent
        #fields = ('id', 'created_at', 'updated_at' )


class PartyInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpParty
        fields = ("name", "acronym", "oname",)



class PoliticianInlineSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name = 'politici:politician-detail')
    image_uri = serializers.CharField(source='get_image_uri', read_only=True)

    class Meta:
        model = OpPolitician
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location',
            'self', 'image_uri',
        )


class OpInstitutionChargeSerializer(serializers.ModelSerializer):
    content = OpenContentSerializer()
    politician = PoliticianInlineSerializer()
    party = PartyInlineSerializer()
    institution_descr = serializers.CharField(source='institution')
    charge_type_descr = serializers.CharField(source='charge_type')
    location = serializers.HyperlinkedRelatedField(view_name='territori:location-detail')
    location_descr = serializers.CharField(source='location')
    class Meta:
        model = OpInstitutionCharge
        view_name = 'politici:instcharge-detail'
        fields = (
            'date_start', 'date_end',
            'politician',
            'charge_type_descr', 'institution_descr',
            'location_descr', 'location',
            'description',
            'party',
            'content',
        )

class OpInstitutionChargeInlineSerializer(serializers.HyperlinkedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name = 'politici:instcharge-detail')
    charge = serializers.CharField(source='getExtendedTextualRepresentation')
    class Meta:
        model = OpInstitutionCharge
        view_name = 'politici:instcharge-detail'
        fields = (
            'charge',
        )

class PoliticianSerializer(serializers.HyperlinkedModelSerializer):
    content = ContentSerializer()
    image_uri = serializers.CharField(source='get_image_uri', read_only=True)
    resources = ResourceSerializer(many=True)
    institution_charges = OpInstitutionChargeInlineSerializer(many=True)
    class Meta:
        model = OpPolitician
        view_name = 'politici:politician-detail'
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location',
            'last_charge_update',
            'content', 'image_uri',
            'resources',
            'institution_charges'
        )

