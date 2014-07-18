from popolo.models import Person
from rest_framework import serializers, pagination

__author__ = 'guglielmo'

class PersonSerializer(serializers.HyperlinkedModelSerializer):
    identifiers = serializers.RelatedField(many=True)
    other_names = serializers.RelatedField(many=True)
    contact_details = serializers.RelatedField(many=True)
    links = serializers.RelatedField(many=True)
    sources = serializers.RelatedField(many=True)

    class Meta:
        model = Person


