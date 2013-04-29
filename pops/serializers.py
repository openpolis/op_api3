__author__ = 'guglielmo'
from pops.models import Person
from rest_framework import serializers


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        read_only_fields = ('first_name', 'last_name', 'birth_date', 'death_date', 'sex')
        fields = ('url',) + read_only_fields

