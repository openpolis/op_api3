from rest_framework import serializers

from op_api.parlamento import models
from op_api.parlamento.fields import HyperlinkedParlamentariField, CaricaField, RamoField


__author__ = 'daniele'


class GruppoSerializer(serializers.ModelSerializer):

    parlamentari_url = HyperlinkedParlamentariField(filter='gruppo')

    class Meta:
        model = models.Gruppo
        fields = ('id', 'nome', 'acronimo', 'parlamentari_url', )


class PoliticoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Politico


class CaricaSerializer(serializers.ModelSerializer):

    tipo_carica = CaricaField()
    #politico = PoliticoSerializer()

    class Meta:
        model = models.Carica
        fields = (
            'id',
            #'carica', 'politico',
            'tipo_carica',
            'data_inizio', 'data_fine',
            'legislatura', 'circoscrizione',
            #'presenze', 'assenze', 'missioni',
            #'indice', 'scaglione', 'posizione', 'media', 'ribelle',
            #'maggioranza_sotto', 'maggioranza_sotto_assente',
            #'maggioranza_salva', 'maggioranza_salva_assente',
            #'parliament_id', 'created_at',
        )


class ParlamentareHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PoliticianHistoryCache
        fields = (
            # "id",
            "legislatura", "data",
            "assenze", "assenze_pos", "assenze_delta",
            "presenze", "presenze_pos", "presenze_delta",
            "missioni", "missioni_pos", "missioni_delta",
            "indice", "indice_pos", "indice_delta",
            "ribellioni", "ribellioni_pos", "ribellioni_delta",
            "ramo",
            #"numero",
            #"chi_tipo", "chi_id", "gruppo_id",
            #"created_at", "updated_at",
            #"carica", "gruppo"
        )


class ParlamentareSerializer(serializers.ModelSerializer):

    carica = CaricaSerializer()
    gruppo = GruppoSerializer()
    anagrafica = PoliticoSerializer(source='carica.politico')
    ramo = RamoField()

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
            # "id",
            #"legislatura", "ramo", "data",
            #"chi_tipo", "chi_id", "gruppo_id",
            #"created_at", "updated_at",
            "anagrafica", "carica", "gruppo"
        ) + statistic_fields
        # fields = (
        #     'id',
        #     'carica', 'politico',
        #     # 'tipo_carica',
        #     'data_inizio', 'data_fine',
        #     'legislatura', 'circoscrizione',
        #     #'presenze', 'assenze', 'missioni',
        #     #'indice', 'scaglione', 'posizione', 'media', 'ribelle',
        #     #'maggioranza_sotto', 'maggioranza_sotto_assente',
        #     #'maggioranza_salva', 'maggioranza_salva_assente',
        #     #'parliament_id', 'created_at',
        # )