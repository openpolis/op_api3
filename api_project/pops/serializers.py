from popolo.models import Person, ContactDetail, Link, Source, Identifier, OtherName, Organization, Post, Membership
from rest_framework import serializers, pagination

__author__ = 'guglielmo'

class GenericRelatableSerializer(object):
    class Meta:
        abstract = True
        exclude = ('id', 'content_type', 'object_id', )

class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta(GenericRelatableSerializer.Meta):
        model = ContactDetail


class LinkSerializer(serializers.ModelSerializer):
    class Meta(GenericRelatableSerializer.Meta):
        model = Link


class SourceSerializer(serializers.ModelSerializer):
    class Meta(GenericRelatableSerializer.Meta):
        model = Source


class IdentifierSerializer(serializers.ModelSerializer):
    class Meta(GenericRelatableSerializer.Meta):
        model = Identifier


class OtherNameSerializer(serializers.ModelSerializer):
    class Meta(GenericRelatableSerializer.Meta):
        model = OtherName


class MembershipSerializer(serializers.HyperlinkedModelSerializer):
    contact_details = ContactDetailSerializer(many=True)
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)

    class Meta:
        model = Membership
        exclude = ('area',)


class MembershipInlineSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = ('label', 'url', 'person', 'post', 'organization')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    contact_details = ContactDetailSerializer(many=True)
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    memberships = MembershipInlineSerializer(many=True)

    class Meta:
        model = Post
        exclude = ('start_date', 'end_date', 'area') # duplicates of birth_date and death_date


class PostInlineSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = ('label', 'url', 'organization')




class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.SlugField()
    identifiers = IdentifierSerializer(many=True)
    other_names = OtherNameSerializer(many=True)
    contact_details = ContactDetailSerializer(many=True)
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    posts = PostInlineSerializer(many=True)
    memberships = MembershipInlineSerializer(many=True)

    class Meta:
        model = Organization
        exclude = ('start_date', 'end_date', 'area') # duplicates of birth_date and death_date


class OrganizationInlineSerializer(OrganizationSerializer):
    class Meta(OrganizationSerializer.Meta):
        fields = ('name', 'url', 'classification', 'founding_date', 'dissolution_date')


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.SlugField()

    json_ld_context = serializers.CharField(
        max_length=255,
        source='json_ld_context',
    )
    json_ld_type = serializers.CharField(
        max_length=255,
        source='json_ld_type',
    )
    json_ld_id = serializers.HyperlinkedIdentityField(view_name='person-detail')

    identifiers = IdentifierSerializer(many=True)
    other_names = OtherNameSerializer(many=True)
    contact_details = ContactDetailSerializer(many=True)
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    memberships = MembershipInlineSerializer(many=True)

    class Meta:
        model = Person
        exclude = ('start_date', 'end_date') # duplicates of birth_date and death_date


class PersonInlineSerializer(PersonSerializer):
    class Meta(PersonSerializer.Meta):
        fields = ('json_ld_context', 'json_ld_type', 'json_ld_id', 'name', 'url', 'gender', 'birth_date', 'death_date')
