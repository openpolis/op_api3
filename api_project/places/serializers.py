# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.reverse import reverse
from places.fields import HyperlinkedTreeNodeField, HyperlinkedTreeNodeManyField, ClassificationTreeTagFromURLField
from rest_framework_gis.serializers import GeoModelSerializer
from places.models import Place, PlaceType, PlaceIdentifier, Identifier, PlaceAcronym, PlaceLink, PlaceGEOInfo, \
    PlaceI18Name, Language, ClassificationTreeTag, ClassificationTreeNode

__author__ = 'guglielmo'






class PlaceTypeSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:placetype-detail')

    def to_native(self, obj):
        """
        This is here only to show how to create _links or _embed sections
        """
        result = super(PlaceTypeSerializer, self).to_native(obj)
        if obj:
            self_url = reverse('maps:placetype-detail',
                               kwargs={'slug': obj.slug},
                               request=self.context['request'],
                               format=self.context['format']
            )
            result.update({
                '_links': {
                    'self': self_url,
                }
            })

        return result

    class Meta:
        model = PlaceType
        fields = ('_self', 'slug', 'name',)
        lookup_field = 'slug'


class LanguageSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:language-detail', lookup_field='iso639_1_code')

    class Meta:
        model = Language
        fields = ('_self', 'iso639_1_code', 'name', 'dbpedia_resource', )


class IdentifierSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:identifier-detail', lookup_field='slug')

    class Meta:
        model = Identifier
        fields = ('_self', 'scheme', 'name', 'slug')



class AcronymInlineSerializer(serializers.ModelSerializer):
    """
    Customize the serializer, allowing to specify acronyms for a place,
    directly as a list of strings: ['RM', 'RM0', ...].

    The from_native and to_native methods are overriden to the avail.
    """
    def get_identity(self, data):
        return data

    def to_native(self, value):
        return '%s' % (value.acronym, )

    def from_native(self, data, files):
        value =  super(AcronymInlineSerializer, self).from_native({'acronym': data}, files)
        return value

    class Meta:
        model = PlaceAcronym
        fields = ('acronym',)

class LinkInlineSerializer(serializers.ModelSerializer):
    """
    Inline serializer for the web pages of a given Place
    """
    def get_identity(self, data):
        return data['uri']

    class Meta:
        model = PlaceLink
        fields = ('uri', 'text')

class GeoInfoInlinseSerializer(GeoModelSerializer):
    """
    Inline serializer for the geographic information related to the Place
    """
    def get_identity(self, data):
        return "{0}:{1}".format(data['gps_lat'], data['gps_lon'])

    class Meta:
        model = PlaceGEOInfo
        fields = ('gps_lat', 'gps_lon', 'geom',)


class NameInlineSerializer(serializers.ModelSerializer):
    """
    Inline serializer for the I18N Names of the Place
    """
    language = serializers.HyperlinkedRelatedField(view_name='maps:language-detail', lookup_field='iso639_1_code')

    def get_identity(self, data):
        return u"{0}".format(data['name'])

    class Meta:
        model = PlaceI18Name
        fields = ('language', 'name', )


class PlaceIdentifierSerializer(serializers.ModelSerializer):
    identifier = serializers.HyperlinkedRelatedField(view_name='maps:identifier-detail', lookup_field='slug')

    def get_identity(self, data):
        return u"{0}".format(data['identifier'],)

    class Meta:
        model = PlaceIdentifier
        fields = ('identifier', 'value', )


class PlaceInlineSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:place-detail')
    place_type = serializers.HyperlinkedRelatedField(view_name='maps:placetype-detail')

    class Meta:
        model = Place
        view_name = 'maps:place-list'
        fields = (
            '_self', 'slug', 'name', 'inhabitants', 'start_date', 'end_date', 'place_type',
        )


class PlaceSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:place-detail')
    place_type = serializers.HyperlinkedRelatedField(view_name='maps:placetype-detail')

    acronyms = AcronymInlineSerializer(many=True, allow_add_remove=True)
    links = LinkInlineSerializer(many=True, allow_add_remove=True)
    geoinfo = GeoInfoInlinseSerializer()

    placeidentifiers = PlaceIdentifierSerializer(many=True, allow_add_remove=True)
    names = NameInlineSerializer(many=True, allow_add_remove=True)

    class Meta:
        model = Place
        view_name = 'maps:place-detail'
        lookup_field = 'slug'
        fields = (
            '_self',
            'slug', 'name', 'inhabitants', 'start_date', 'end_date',
            'place_type',
            'acronyms', 'links', 'geoinfo',
            'placeidentifiers', 'names'
        )


class ClassificationTreeTagSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:classification-detail')
    root_node = HyperlinkedTreeNodeField(source='get_root_node')

    class Meta:
        model = ClassificationTreeTag
        fields = (
            '_self', 'slug', 'label', 'description', 'root_node'
        )

class ClassificationTreeTagFromURLSerializer(serializers.ModelSerializer):
    _self = serializers.HyperlinkedIdentityField(view_name='maps:classification-detail')
    root_node = HyperlinkedTreeNodeField(source='get_root_node')

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        # override the object, taking it from the url and not from the view
        if 'tag__slug' in self.context['view'].kwargs:
            tag_slug = self.context['view'].kwargs['tag__slug']
            obj = ClassificationTreeTag.objects.get(slug=tag_slug)

        return super(ClassificationTreeTagFromURLSerializer, self).to_native(obj)


    class Meta:
        model = ClassificationTreeTag
        fields = (
            '_self', 'slug', 'label', 'description', 'root_node'
        )

class ClassificationTreeNodeInlineSerializer(serializers.ModelSerializer):
    place = serializers.HyperlinkedRelatedField(view_name='maps:place-detail')
    tag = serializers.HyperlinkedRelatedField(view_name='maps:classification-detail')

    class Meta:
        model = ClassificationTreeNode
        fields = (
            'place',
        )


class ClassificationTreeNodeSerializer(serializers.Serializer):
    place = PlaceInlineSerializer()
    tag = ClassificationTreeTagFromURLSerializer()
    parent = HyperlinkedTreeNodeField(source='parent')
    ancestors = HyperlinkedTreeNodeManyField(source='ancestors_slugs')
    children = HyperlinkedTreeNodeManyField(source='children_slugs')
