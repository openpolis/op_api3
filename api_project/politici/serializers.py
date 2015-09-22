from rest_framework import serializers

from politici.models import OpUser, OpResources, OpPolitician, OpContent, OpInstitutionCharge, OpOpenContent, \
    OpParty, OpGroup, \
    OpEducationLevel, OpProfession, OpPoliticianHasOpEducationLevel


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

class GroupInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpGroup
        fields = ("name", "acronym", "oname",)

class EducationLevelSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='normalized_description', read_only=True)
    class Meta:
        model = OpEducationLevel
        fields = ('description',)

class OpPoliticianHasOpEducationLevelSerializer(serializers.ModelSerializer):
    education_level = EducationLevelSerializer()
    class Meta:
        model = OpPoliticianHasOpEducationLevel
        fields = ('description', 'education_level')


class ProfessionSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='normalized_description', read_only=True)

    class Meta:
        model = OpProfession
        fields = ("description",)




class PoliticianInlineSerializer(serializers.ModelSerializer):
    self_uri = serializers.HyperlinkedIdentityField(view_name = 'politici:politician-detail')
    image_uri = serializers.CharField(source='get_image_uri', read_only=True)
    profession = ProfessionSerializer()
    education_levels = OpPoliticianHasOpEducationLevelSerializer(many=True)
    content = ContentSerializer()

    class Meta:
        model = OpPolitician
        fields = (
            'content',
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location', 'sex',
            'self_uri', 'image_uri',
            'profession',
            'education_levels',
        )


class OpInstitutionChargeSerializer(serializers.ModelSerializer):
    content = OpenContentSerializer()
    politician = PoliticianInlineSerializer()
    party = PartyInlineSerializer()
    group = GroupInlineSerializer()
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
            'party', 'group',
            'content',
        )

class OpInstitutionChargeInlineSerializer(serializers.HyperlinkedModelSerializer):
    self_uri = serializers.HyperlinkedIdentityField(view_name = 'politici:instcharge-detail')
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
    profession = ProfessionSerializer()
    resources = ResourceSerializer(many=True)
    education_levels = OpPoliticianHasOpEducationLevelSerializer(many=True)
    institution_charges = OpInstitutionChargeInlineSerializer(many=True)
    class Meta:
        model = OpPolitician
        view_name = 'politici:politician-detail'
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location', 'sex',
            'last_charge_update',
            'content', 'image_uri',
            'profession', 'education_levels',
            'resources',
            'institution_charges',
            'profession',
            'education_levels',
        )

