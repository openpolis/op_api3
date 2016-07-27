from __future__ import unicode_literals

from django.db import models


class Carica(models.Model):
    politician = models.ForeignKey('Politico', db_column='politico_id')
    charge_type = models.ForeignKey('TipoCarica', db_column='tipo_carica_id')
    charge = models.CharField(max_length=30L, blank=True, db_column='carica')
    start_date = models.DateField(null=True, blank=True, db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    #legislatura = models.IntegerField(null=True, blank=True)
    district = models.CharField(max_length=60L, blank=True, db_column='circoscrizione')
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
        managed = False


class CaricaHasGruppo(models.Model):
    charge = models.ForeignKey(Carica, db_column='carica')
    group = models.ForeignKey('Gruppo', db_column='gruppo')
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    presenze = models.IntegerField(null=True, blank=True)
    ribelle = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'opp_carica_has_gruppo'
        managed = False


class Gruppo(models.Model):
    
    name = models.CharField(max_length=255L, blank=True, db_column='nome')
    acronym = models.CharField(max_length=80L, blank=True, db_column='acronimo')

    parliamentarians = models.ManyToManyField(Carica, through=CaricaHasGruppo, related_name='groups')

    class Meta:
        db_table = 'opp_gruppo'
        managed = False


class GruppoIsMaggioranza(models.Model):
    
    group = models.ForeignKey(Gruppo, db_column='group')
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    maggioranza = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_is_maggioranza'
        managed = False


class GruppoRamo(models.Model):
    
    group = models.ForeignKey(Gruppo, db_column='group')
    house = models.CharField(max_length=1L, blank=True, db_column='ramo')
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    #parlamento_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_ramo'
        managed = False





class CaricaInterna(models.Model):
    carica = models.ForeignKey(OppCarica)
    tipo_carica = models.ForeignKey('OppTipoCarica')
    sede = models.ForeignKey('OppSede')
    data_inizio = models.DateField(blank=True, null=True)
    data_fine = models.DateField(blank=True, null=True)
    descrizione = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = 'opp_carica_interna'
        managed = False


class TipoCarica(models.Model):    
    name = models.CharField(max_length=255L, blank=True, db_column='nome')

    class Meta:
        db_table = 'opp_tipo_carica'
        managed = False


class Sede(models.Model):
    ramo = models.CharField(max_length=255, blank=True)
    denominazione = models.CharField(max_length=255, blank=True)
#    legislatura = models.IntegerField(blank=True, null=True)
    tipologia = models.CharField(max_length=255, blank=True)
    codice = models.CharField(max_length=255, blank=True)
    data_inizio = models.DateField(blank=True, null=True)
    data_fine = models.DateField(blank=True, null=True)
    parlamento_id = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'opp_sede'
        managed = False


class PoliticianHistoryCache(models.Model):
    
    #legislatura = models.IntegerField(null=True, blank=True)
    update_date = models.DateField(db_column='data')
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
    house = models.CharField(max_length=1L, db_column='ramo')
    #gruppo_id = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    charge = models.ForeignKey(Carica, blank=True, null=True, db_column='chi_id', related_name='+')
    group = models.ForeignKey(Gruppo, null=True, blank=True, db_column='gruppo_id', related_name='charges+')

    @property
    def politico(self):
        return self.carica.politico

    class Meta:
        db_table = 'opp_politician_history_cache'
        ordering = ('charge__politician__surname', 'charge__politician__name')
        managed = False


class Politico(models.Model):
    name = models.CharField(max_length=30L, blank=True, db_column='nome')
    surname = models.CharField(max_length=30L, blank=True, db_column='cognome')
    gender = models.CharField(max_length=1L, blank=True, db_column='sesso')
    monitoring_users = models.IntegerField(db_column='n_monitoring_users')

    class Meta:
        db_table = 'opp_politico'
        managed = False



class Seduta(models.Model):
    date = models.DateField(null=True, blank=True, db_column='data')
    number = models.IntegerField(db_column='numero')
    house = models.CharField(max_length=1L, db_column='ramo')
    #legislatura = models.IntegerField()
    reference_url = models.TextField(blank=True, db_column='url')
    is_imported = models.IntegerField()

    class Meta:
        db_table = 'opp_seduta'
        managed = False


class Votazione(models.Model):

    sitting = models.ForeignKey(Seduta, db_column='seduta_id', related_name='votes')
    charge_set = models.ManyToManyField(Carica, through='VotazioneHasCarica')

    numero_votazione = models.IntegerField()
    titolo = models.TextField(blank=True)
    titolo_aggiuntivo = models.TextField(blank=True)
    presenti = models.IntegerField(null=True, blank=True)
    votanti = models.IntegerField(null=True, blank=True)
    maggioranza = models.IntegerField(null=True, blank=True)
    astenuti = models.IntegerField(null=True, blank=True)
    favorevoli = models.IntegerField(null=True, blank=True)
    contrari = models.IntegerField(null=True, blank=True)
    esito = models.CharField(max_length=20L, blank=True)
    ribelli = models.IntegerField(null=True, blank=True)
    margine = models.IntegerField(null=True, blank=True)
    tipologia = models.CharField(max_length=20L, blank=True)
    descrizione = models.TextField(blank=True)
    url = models.CharField(max_length=255L, blank=True)
    finale = models.IntegerField()
    nb_commenti = models.IntegerField()
    is_imported = models.IntegerField()
    ut_fav = models.IntegerField()
    ut_contr = models.IntegerField()
    is_maggioranza_sotto_salva = models.IntegerField()

    class Meta:
        db_table = 'opp_votazione'
        ordering = ('numero_votazione', )
        managed = False


class VotazioneHasCarica(models.Model):
    vote = models.ForeignKey(Votazione, db_column='votazione_id')
    charge = models.ForeignKey(Carica, db_column='carica_id')
    voting = models.CharField(max_length=40L, blank=True, db_column='voto')
    rebel = models.IntegerField(db_column='ribelle')
    maggioranza_sotto_salva = models.IntegerField()

    class Meta:
        db_table = 'opp_votazione_has_carica'
        managed = False

