from popolo.models import Person, ContactDetail, Link, Source, Identifier, OtherName, Organization, Post, Membership, \
    Area
from rest_framework import serializers, pagination

__author__ = 'guglielmo'

class GenericRelatableSerializer(object):
    class Meta:
        abstract = True
        exclude = ('id', 'content_type', 'object_id', )

class ContactDetailSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='contact_type')
    class Meta(GenericRelatableSerializer.Meta):
        exclude = ('contact_type', )
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
    area_id = serializers.SlugField(source='area.id')
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    organization_id = serializers.SlugField(source='organization.id')
    on_behalf_of_id = serializers.SlugField(source='on_behalf_of.id')
    person_id = serializers.SlugField(source='person.id')
    post_id = serializers.SlugField(source='post.id')

    class Meta:
        model = Membership
        exclude = ('area',)
        fields = ('id', 'label', 'role',
                  'person_id', 'person',
                  'post_id', 'post',
                  'organization_id', 'organization',
                  'area_id', 'area',
                  'start_date', 'end_date',
                  'on_behalf_of_id', 'on_behalf_of',
                  'contact_details', 'links', 'sources',
                  'url')

class MembershipInlineSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = ('id', 'label', 'role',
                  'person_id', 'post_id', 'organization_id', 'on_behalf_of_id', 'area_id',
                  'url')

class MembershipListSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = ('id', 'label',
                  'person_id', 'post_id', 'organization_id', 'area_id',
                  'on_behalf_of_id',
                  'start_date', 'end_date',
                  'contact_details', 'links', 'sources', 'url',
                  'created_at', 'updated_at')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    contact_details = ContactDetailSerializer(many=True)
    organization_id = serializers.SlugField(source='organization.id')
    area_id = serializers.SlugField(source='area.id')
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    memberships = MembershipInlineSerializer(many=True)

    class Meta:
        model = Post
        exclude = ('start_date', 'end_date', 'area', 'memberships') # duplicates of birth_date and death_date


class PostInlineSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = ('id', 'role', 'organization_id',
                  'area_id',
                  'label', 'other_label',
                  'contact_details', 'links', 'sources',
                  'created_at', 'updated_at',
                  'url')




class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.SlugField()
    parent_id = serializers.SlugField(source='parent.id')
    area_id = serializers.SlugField(source='area.id')
    identifiers = IdentifierSerializer(many=True)
    other_names = OtherNameSerializer(many=True)
    contact_details = ContactDetailSerializer(many=True)
    links = LinkSerializer(many=True)
    sources = SourceSerializer(many=True)
    memberships = MembershipInlineSerializer(many=True)

    class Meta:
        model = Organization
        fields = (
            'id',
            'name', 'other_names', 'identifiers',
            'classification',
            'parent_id', 'parent',
            'area_id', 'area',
            'founding_date', 'dissolution_date',
            'image', 'contact_details',
            'memberships',
            'links', 'sources',
            'url'
        )

class OrganizationInlineSerializer(OrganizationSerializer):
    class Meta(OrganizationSerializer.Meta):
        fields = ('id',
            'name', 'other_names', 'identifiers',
            'classification', 'parent_id',
            'area_id',
            'founding_date', 'dissolution_date',
            'image', 'contact_details',
            'links', 'sources',
            'created_at', 'updated_at',
            'url'
        )


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
        fields = (
            'json_ld_context', 'json_ld_type',
            'id', 'name', 'family_name', 'given_name',
            'additional_name', 'sort_name', 'patronymic_name',
            'honorific_prefix', 'honorific_suffix',
            'url', 'email',
            'gender', 'birth_date', 'death_date',
            'image',
            'summary', 'biography', 'national_identity',
            'other_names',
            'identifiers',
            'contact_details',
            'memberships',
            'links', 'sources'
        )

# only kept to study json_ld_* fields, to be used later
class PersonInlineSerializer(PersonSerializer):
    class Meta(PersonSerializer.Meta):
        fields = (
            'json_ld_context',      'json_ld_type',
            'id', 'name', 'family_name', 'given_name',
            'additional_name', 'sort_name', 'patronymic_name',
            'honorific_prefix', 'honorific_suffix',
            'url', 'email',
            'gender', 'birth_date', 'death_date',
            'image',
            'summary', 'biography', 'national_identity',
            'other_names',
            'identifiers',
            'contact_details',
            'links', 'sources',
            'created_at', 'updated_at',
        )



class AreaSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.SlugField(source='id')
    parent_id = serializers.IntegerField(source='parent.id')
    other_identifiers = IdentifierSerializer(many=True)
    sources = SourceSerializer(many=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'classification', 'identifier',
                  'inhabitants', 'start_date', 'end_date',
                  'parent_id', 'other_identifiers', 'sources',
                  'url')
