from rest_framework import serializers
from rest_framework import pagination

from parlamento import models
from parlamento import fields


__author__ = 'daniele'


class GruppoSerializer(serializers.ModelSerializer):

    parliamentarians_uri = fields.HyperlinkedParlamentariField(filter='group')

    class Meta:
        model = models.Gruppo
        fields = ('id', 'name', 'acronym', 'parliamentarians_uri', )


class SedeSerializer(serializers.ModelSerializer):
    parliamentarians_uri = fields.HyperlinkedParlamentariField(filter='site')

    class Meta:
        model = models.Sede
        fields = ('id', 'house', 'name', 'site_type', 'code', 'start_date',
                  'end_date', 'parliamentarians_uri')


class PoliticoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Politico
        fields = ('id', 'name', 'surname', 'gender', 'monitoring_users', )


class CaricaInlineSerializer(serializers.HyperlinkedModelSerializer):

    charge_type = fields.UnicodeField()
    group = fields.UnicodeField()
    politician = fields.UnicodeField(source='politician')
    house = fields.RamoField()

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            "politician", "charge_type"
        )


class CaricaSerializer(serializers.ModelSerializer):

    charge_type = fields.CaricaField()

    class Meta:
        model = models.Carica
        fields = ('id', 'charge_type', 'start_date', 'end_date', 'district', 'parliament_id' )


class CaricaInternaSerializer(serializers.ModelSerializer):
    site = fields.UnicodeField()
    site_parliamentarians_uri = fields.HyperlinkedParlamentariField(
        filter='site', field_name='site_id'
    )
    charge_type = fields.CaricaField()

    class Meta:
        model = models.CaricaInterna
        fields = ('charge_type', 'site', 'site_parliamentarians_uri',
                  'start_date',
                  'end_date' )


class ParlamentareInlineSerializer(serializers.HyperlinkedModelSerializer):
    self_unicode = serializers.CharField(source='__unicode__')
    self_uri = fields.HyperlinkedParlamentareIdentityField()
    parliamentary_charge = fields.FirstParliamentarianChargeField(
        source='charges'
    )


    # group = fields.UnicodeField()
    # politician = fields.UnicodeField(source='charge.politician')
    # house = fields.RamoField()

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            "self_unicode", "self_uri", "parliamentary_charge"
        )


class ParlamentareCacheInlineSerializer(serializers.HyperlinkedModelSerializer):
    self_url = fields.HyperlinkedParlamentareCacheIdentityField(
        view_name='parlamento:parlamentare-cache-detail',
        lookup_field='chi_id'
    )
    charge = fields.UnicodeField()
    group = fields.UnicodeField()
    politician = fields.UnicodeField(source='charge.politician')
    house = fields.RamoField()

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            "politician", "charge", "group", "house", "self_url"
        )

class ParlamentareCacheSerializer(serializers.ModelSerializer):
    charge = CaricaSerializer()
    inner_charges = CaricaInternaSerializer(many=True, source='charge.innercharges')
    group = GruppoSerializer()
    politician = PoliticoSerializer(source='charge.politician')
    house = fields.RamoField()

    def to_native(self, obj):
        ret = super(ParlamentareCacheSerializer, self).to_native(obj)

        stats = {}
        for field in self.Meta.statistic_fields:
            stats[field] = ret[field]
            del ret[field]
        ret['statistics'] = stats
        return ret

    class Meta:
        model = models.PoliticianHistoryCache
        statistic_fields = (
            "assenze", "assenze_pos", "assenze_delta",
            "presenze", "presenze_pos", "presenze_delta",
            "missioni", "missioni_pos", "missioni_delta",
            "indice", "indice_pos", "indice_delta",
            "ribellioni", "ribellioni_pos", "ribellioni_delta",
            "numero",
        )
        fields = (
            "politician", "charge", "group", "inner_charges"
        ) + statistic_fields


class CustomPaginationSerializer(pagination.PaginationSerializer):

    legislative_session = fields.LegislaturaField(source='*')


class SedutaSerializer(serializers.ModelSerializer):

    votes = fields.HyperlinkedVotazioneField(many=True)

    class Meta:
        model = models.Seduta
        depth = 0
        fields = ('id', 'date', 'number', 'house', 'reference_url', 'is_imported', 'votes', )


class VotazioneSerializer(serializers.ModelSerializer):

    votazione_uri = fields.HyperlinkedVotazioneIdentityField()
    seduta = fields.HyperlinkedSedutaField(read_only=True)

    class Meta:
        model = models.Votazione
        fields = (
            'id', 'sitting', 'votazione_uri',
            'numero_votazione',
            'titolo', 'titolo_aggiuntivo', 'descrizione',
            'presenti', 'votanti', 'maggioranza', 'astenuti',
            'favorevoli', 'contrari', 'esito', 'ribelli',
            'margine', 'tipologia',
            'finale', 'nb_commenti',
            'ut_fav', 'ut_contr', 'is_maggioranza_sotto_salva',
            'is_imported', 'url'
        )


class VotoSerializer(serializers.ModelSerializer):
    politician = serializers.IntegerField(source='charge__politician')

    class Meta:
        model = models.VotazioneHasCarica
        fields = (
            'politician', 'voting', 'rebel', 'maggioranza_sotto_salva',
        )


class VotazioneDettagliataSerializer(serializers.ModelSerializer):

    charge_votes = VotoSerializer(many=True, source='dettagli')
    vote_uri = fields.HyperlinkedVotazioneIdentityField()
    sitting = fields.HyperlinkedSedutaField(read_only=True)

    class Meta:
        model = models.Votazione
        fields = (
            'sitting', 'vote_uri',
            'numero_votazione',
            'titolo', 'titolo_aggiuntivo', 'descrizione',
            'presenti', 'votanti', 'maggioranza', 'astenuti',
            'favorevoli', 'contrari', 'esito', 'ribelli',
            'margine', 'tipologia',
            'finale', 'nb_commenti',
            'ut_fav', 'ut_contr', 'is_maggioranza_sotto_salva',
            'is_imported', 'url', 'charge_votes',
        )


