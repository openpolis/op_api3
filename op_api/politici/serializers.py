from rest_framework import serializers

from op_api.politici.models import OpUser, OpPolitician, OpContent


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpUser
        view_name = 'politici-user-detail'
        fields = ('url', 'first_name', 'last_name', 'nickname', 'is_active', 'email')


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpContent
        fields = ('id', 'created_at', 'updated_at' )

class PoliticianSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    class Meta:
        model = OpPolitician
        view_name = 'politici-politician-detail'
        fields = (
            'first_name', 'last_name',
            'birth_date', 'death_date', 'birth_location',
            'last_charge_update',
            'content',
        )

