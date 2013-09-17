from rest_framework import serializers
from rest_framework import pagination

from op_api.parlamento import models
from op_api.parlamento import fields


__author__ = 'daniele'


class GruppoSerializer(serializers.ModelSerializer):

    parlamentari_url = fields.HyperlinkedParlamentariField(filter='gruppo')

    class Meta:
        model = models.Gruppo
        fields = ('id', 'nome', 'acronimo', 'parlamentari_url', )


class PoliticoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Politico


class CaricaSerializer(serializers.ModelSerializer):

    tipo_carica = fields.CaricaField()
    #politico = PoliticoSerializer()

    class Meta:
        model = models.Carica
        fields = (
            'id',
            'tipo_carica',
            'data_inizio', 'data_fine',
            'legislatura', 'circoscrizione',
        )


class ParlamentareHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            "legislatura", "data",
            "assenze", "assenze_pos", "assenze_delta",
            "presenze", "presenze_pos", "presenze_delta",
            "missioni", "missioni_pos", "missioni_delta",
            "indice", "indice_pos", "indice_delta",
            "ribellioni", "ribellioni_pos", "ribellioni_delta",
            "ramo",
        )


class CustomPaginationSerializer(pagination.PaginationSerializer):

    legislatura = fields.LegislaturaField(source='*')
    data = fields.UltimoAggiornamentoField(source='*')


class ParlamentareSerializer(serializers.ModelSerializer):

    carica = CaricaSerializer()
    gruppo = GruppoSerializer()
    anagrafica = PoliticoSerializer(source='carica.politico')
    ramo = fields.RamoField()

    def to_native(self, obj):
        ret = super(ParlamentareSerializer, self).to_native(obj)

        stats = {}
        for field in self.Meta.statistic_fields:
            stats[field] = ret[field]
            del ret[field]
        ret['statistiche'] = stats
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
            "anagrafica", "carica", "gruppo"
        ) + statistic_fields


class SedutaSerializer(serializers.ModelSerializer):

    votazione_set = fields.HyperlinkedVotazioneField(many=True)

    class Meta:
        model = models.Seduta
        depth = 0
        fields = (
            'id', 'data', 'numero', 'ramo',
            #'legislatura',
            'url', 'is_imported',
            'votazione_set',
        )


class VotazioneSerializer(serializers.ModelSerializer):

    carica_set = fields.HyperlinkedParlamentareField(read_only=True, many=True)
    seduta = fields.HyperlinkedSedutaField(read_only=True)

    class Meta:
        model = models.Votazione
        fields = (
            'id', 'seduta',
            'numero_votazione',
            'titolo', 'titolo_aggiuntivo', 'descrizione',
            'presenti', 'votanti', 'maggioranza', 'astenuti',
            'favorevoli', 'contrari', 'esito', 'ribelli',
            'margine', 'tipologia',
            'finale', 'nb_commenti',
            'ut_fav', 'ut_contr', 'is_maggioranza_sotto_salva',
            'is_imported', 'url', 'carica_set',
        )