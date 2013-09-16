from __future__ import unicode_literals

from django.contrib.gis.db import models


class Carica(models.Model):
    politico = models.ForeignKey('Politico')
    tipo_carica = models.ForeignKey('TipoCarica')
    carica = models.CharField(max_length=30L, blank=True)
    data_inizio = models.DateField(null=True, blank=True)
    data_fine = models.DateField(null=True, blank=True)
    legislatura = models.IntegerField(null=True, blank=True)
    circoscrizione = models.CharField(max_length=60L, blank=True)
    presenze = models.IntegerField(null=True, blank=True)
    assenze = models.IntegerField(null=True, blank=True)
    missioni = models.IntegerField(null=True, blank=True)
    parliament_id = models.IntegerField(null=True, blank=True)
    indice = models.FloatField(null=True, blank=True)
    scaglione = models.IntegerField(null=True, blank=True)
    posizione = models.IntegerField(null=True, blank=True)
    media = models.FloatField(null=True, blank=True)
    ribelle = models.IntegerField(null=True, blank=True)
    maggioranza_sotto = models.IntegerField()
    maggioranza_sotto_assente = models.IntegerField()
    maggioranza_salva = models.IntegerField()
    maggioranza_salva_assente = models.IntegerField()
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'opp_carica'


class CaricaHasGruppo(models.Model):
    carica = models.ForeignKey(Carica)
    gruppo = models.ForeignKey('Gruppo')
    data_inizio = models.DateField()
    data_fine = models.DateField(null=True, blank=True)
    presenze = models.IntegerField(null=True, blank=True)
    ribelle = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'opp_carica_has_gruppo'


class Gruppo(models.Model):
    
    nome = models.CharField(max_length=255L, blank=True)
    acronimo = models.CharField(max_length=80L, blank=True)

    parlamentari = models.ManyToManyField(Carica, through=CaricaHasGruppo, related_name='gruppi')

    class Meta:
        db_table = 'opp_gruppo'


class GruppoIsMaggioranza(models.Model):
    
    gruppo = models.ForeignKey(Gruppo)
    data_inizio = models.DateField()
    data_fine = models.DateField(null=True, blank=True)
    maggioranza = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_is_maggioranza'


class GruppoRamo(models.Model):
    
    gruppo = models.ForeignKey(Gruppo)
    ramo = models.CharField(max_length=1L, blank=True)
    data_inizio = models.DateField()
    data_fine = models.DateField(null=True, blank=True)
    parlamento_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_ramo'


class PoliticianHistoryCache(models.Model):
    
    legislatura = models.IntegerField(null=True, blank=True)
    data = models.DateField()
    assenze = models.FloatField(null=True, blank=True)
    assenze_pos = models.IntegerField(null=True, blank=True)
    assenze_delta = models.FloatField(null=True, blank=True)
    presenze = models.FloatField(null=True, blank=True)
    presenze_pos = models.IntegerField(null=True, blank=True)
    presenze_delta = models.FloatField(null=True, blank=True)
    missioni = models.FloatField(null=True, blank=True)
    missioni_pos = models.IntegerField(null=True, blank=True)
    missioni_delta = models.FloatField(null=True, blank=True)
    indice = models.FloatField(null=True, blank=True)
    indice_pos = models.IntegerField(null=True, blank=True)
    indice_delta = models.FloatField(null=True, blank=True)
    ribellioni = models.FloatField(null=True, blank=True)
    ribellioni_pos = models.IntegerField(null=True, blank=True)
    ribellioni_delta = models.FloatField(null=True, blank=True)
    chi_tipo = models.CharField(max_length=1L)
    chi_id = models.IntegerField()
    ramo = models.CharField(max_length=1L)
    gruppo_id = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    carica = models.ForeignKey(Carica, blank=True, null=True, db_column='chi_id', related_name='+')
    gruppo = models.ForeignKey(Gruppo, null=True, blank=True, db_column='gruppo_id', related_name='incarichi+')

    @property
    def politico(self):
        return self.carica.politico

    class Meta:
        db_table = 'opp_politician_history_cache'


class Politico(models.Model):
    nome = models.CharField(max_length=30L, blank=True)
    cognome = models.CharField(max_length=30L, blank=True)
    sesso = models.CharField(max_length=1L, blank=True)
    n_monitoring_users = models.IntegerField()

    class Meta:
        db_table = 'opp_politico'


class TipoCarica(models.Model):
    
    nome = models.CharField(max_length=255L, blank=True)

    class Meta:
        db_table = 'opp_tipo_carica'

