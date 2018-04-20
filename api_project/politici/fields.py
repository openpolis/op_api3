from rest_framework import serializers

from parlamento.utils import reverse_url


class HyperlinkedParlamentareIdentityField(serializers.HyperlinkedIdentityField):
    """
    A hyperlinked-identity field used to build the uri of a parliamentarian.

    This is only valid for the 17th legislatura, as the 16th db did not
    follow some database fields variations.
    """
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({
            'view_name': 'parlamentare-detail',
        })
        super(
            HyperlinkedParlamentareIdentityField, self
        ).__init__(*args, **kwargs)

    def get_url(self, obj, view_name, request, format):
        return reverse_url(
            view_name, request, format=format,
            kwargs={
                'politician_id': obj.pk,
                'legislatura': 18, # only current legislature can work
            }
        )

