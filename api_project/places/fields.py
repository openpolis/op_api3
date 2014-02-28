from rest_framework import serializers
from rest_framework.reverse import reverse

__author__ = 'guglielmo'

class HyperlinkedTreeNodeManyField(serializers.Field):
    """
    Serialize all children's hyperlinks of a ClassificationTreeNode using an optimized values_list query,
    to minimize the number of queries.
    """
    def to_native(self, obj):
        request = self.context['request']
        format = self.context['format']
        ret = []
        for t in obj:
            slugs = {
                'tag__slug': self.context['view'].kwargs['tag__slug'],
                'place__slug': t[0] if t[0] else t[2]
            }
            ret.append(reverse('maps:classificationnode-detail', kwargs=slugs, request=request, format=format))
        return ret


class HyperlinkedTreeNodeField(serializers.Field):
    """
    Return the hyperlink to the ClassificationTreeNode,
    according to the tag__slug and place__slug
    syntax
    """
    def to_native(self, obj):
        request = self.context['request']
        format = self.context['format']
        if obj:
            slugs = {
                'place__slug': obj.place.slug
            }
            if 'tag__slug' in self.context['view'].kwargs:
                slugs['tag__slug'] = self.context['view'].kwargs['tag__slug']
            else:
                slugs['tag__slug'] = obj.tag.slug

            return reverse('maps:classificationnode-detail', kwargs=slugs, request=request, format=format)
        else:
            return None

class ClassificationTreeTagFromURLField(serializers.Field):
    def to_native(self, obj):
        request = self.context['request']
        format = self.context['format']
        tag_slug = self.context['view'].kwargs['tag__slug']
        return reverse('maps:classification-detail', kwargs={'slug': tag_slug}, request=request, format=format)
