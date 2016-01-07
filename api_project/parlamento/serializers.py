from rest_framework import serializers
from rest_framework import pagination

from parlamento import models
from parlamento import fields


__author__ = 'daniele'


class GruppoSerializer(serializers.ModelSerializer):

    parliamentarians_url = fields.HyperlinkedParlamentariField(filter='group')

    class Meta:
        model = models.Gruppo
        fields = ('id', 'name', 'acronym', 'parliamentarians_url', )


class PoliticoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Politico


class CaricaSerializer(serializers.ModelSerializer):

    charge_type = fields.CaricaField()

    class Meta:
        model = models.Carica
        fields = ('id', 'charge_type', 'start_date', 'end_date', 'district', 'parliament_id' )


class ParlamentareHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            "update_date",
            "assenze", "assenze_pos", "assenze_delta",
            "presenze", "presenze_pos", "presenze_delta",
            "missioni", "missioni_pos", "missioni_delta",
            "indice", "indice_pos", "indice_delta",
            "ribellioni", "ribellioni_pos", "ribellioni_delta",
            "house",
        )



class ParlamentareSerializer(serializers.ModelSerializer):
    charge = CaricaSerializer()
    group = GruppoSerializer()
    politician = PoliticoSerializer(source='charge.politician')
    house = fields.RamoField()

    def to_native(self, obj):
        ret = super(ParlamentareSerializer, self).to_native(obj)

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
            "politician", "charge", "group"
        ) + statistic_fields


class CustomPaginationSerializer(pagination.PaginationSerializer):

    legislative_session = fields.LegislaturaField(source='*')
    update_date = fields.UltimoAggiornamentoField(source='*')

    #class Meta:
    #    object_serializer_class = ParlamentareSerializer


class SedutaSerializer(serializers.ModelSerializer):

    votes = fields.HyperlinkedVotazioneField(many=True)

    class Meta:
        model = models.Seduta
        depth = 0
        fields = ('id', 'date', 'number', 'house', 'reference_url', 'is_imported', 'votes', )


class VotazioneSerializer(serializers.ModelSerializer):

    votazione_url = fields.HyperlinkedVotazioneIdentityField()
    seduta = fields.HyperlinkedSedutaField(read_only=True)

    class Meta:
        model = models.Votazione
        fields = (
            'id', 'sitting', 'votazione_url',
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

    class Meta:
        model = models.VotazioneHasCarica
        fields = (
            'charge', 'voting', 'rebel', 'maggioranza_sotto_salva',
        )


class VotazioneDettagliataSerializer(serializers.ModelSerializer):

    charge_votes = VotoSerializer(many=True, source='votazionehascarica_set')
    vote_url = fields.HyperlinkedVotazioneIdentityField()
    sitting = fields.HyperlinkedSedutaField(read_only=True)

    class Meta:
        model = models.Votazione
        fields = (
            'id', 'sitting', 'vote_url',
            'numero_votazione',
            'titolo', 'titolo_aggiuntivo', 'descrizione',
            'presenti', 'votanti', 'maggioranza', 'astenuti',
            'favorevoli', 'contrari', 'esito', 'ribelli',
            'margine', 'tipologia',
            'finale', 'nb_commenti',
            'ut_fav', 'ut_contr', 'is_maggioranza_sotto_salva',
            'is_imported', 'url', 'charge_votes',
        )


