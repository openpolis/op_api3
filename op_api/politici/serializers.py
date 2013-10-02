from rest_framework import serializers

from op_api.politici.models import OpUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpUser
        read_only_fields = ('first_name', 'last_name', 'nickname', 'is_active', 'email')
        fields = ('url',) + read_only_fields

