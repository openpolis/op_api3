__author__ = 'guglielmo'
from rest_framework import serializers

from op_api.pops_old.models import Person


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        read_only_fields = ('first_name', 'last_name', 'birth_date', 'death_date', 'sex')
        fields = ('url',) + read_only_fields

