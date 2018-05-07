from __future__ import unicode_literals

from django.db import models


class Carica(models.Model):
    politician = models.ForeignKey('Politico', db_column='politico_id' ,
                                   related_name='charges')
    charge_type = models.ForeignKey('TipoCarica', db_column='tipo_carica_id',
                                    related_name='charges')
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

    def __unicode__(self):
        if self.end_date:
            return "{0.charge} - dal {0.start_date} al {0.end_date}".format(self)
        else:
            return "{0.charge} - dal {0.start_date}".format(self)

    class Meta:
        db_table = 'opp_carica'
        managed = False


class CaricaHasGruppo(models.Model):
    charge = models.ForeignKey(Carica, db_column='carica_id')
    group = models.ForeignKey('Gruppo', db_column='gruppo_id')
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

    def __unicode__(self):
        return "{0.name} ({0.acronym})".format(self)

    class Meta:
        db_table = 'opp_gruppo'
        managed = False


class GruppoIsMaggioranza(models.Model):
    group = models.ForeignKey(Gruppo, db_column='group',
                              related_name="majorities")
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    maggioranza = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_is_maggioranza'
        managed = False


class GruppoRamo(models.Model):
    group = models.ForeignKey(Gruppo, db_column='gruppo_id',
                              related_name='houses')
    house = models.CharField(max_length=1L, blank=True, db_column='ramo')
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(null=True, blank=True, db_column='data_fine')
    #parlamento_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'opp_gruppo_ramo'
        managed = False


class IncaricoGruppo(models.Model):
    charge_group = models.ForeignKey(CaricaHasGruppo, db_column='chg_id',
                                     related_name='groupcharges')
    start_date = models.DateField(db_column='data_inizio')
    end_date = models.DateField(blank=True, null=True, db_column='data_fine')
    charge = models.CharField(max_length=60, db_column='incarico')
    class Meta:
        managed = False
        db_table = 'opp_chg_incarico'



class CaricaInterna(models.Model):
    charge = models.ForeignKey(Carica, db_column='carica_id',
                               related_name='innercharges')
    charge_type = models.ForeignKey('TipoCarica', db_column='tipo_carica_id')
    site = models.ForeignKey('Sede', db_column='sede_id',
                             related_name='innercharges')
    start_date = models.DateField(blank=True, null=True, db_column='data_inizio')
    end_date = models.DateField(blank=True, null=True, db_column='data_fine')
#    description = models.CharField(max_length=255, blank=True, db_column='descrizione')
    created_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        if self.end_date:
            return "{0.charge_type} - dal {0.start_date} al {0.end_date}".format(self)
        else:
            return "{0.charge_type} - dal {0.start_date}".format(self)

    class Meta:
        db_table = 'opp_carica_interna'
        managed = False


class TipoCarica(models.Model):
    name = models.CharField(max_length=255L, blank=True, db_column='nome')

    def __unicode__(self):
        return "{0.name}".format(self)

    class Meta:
        db_table = 'opp_tipo_carica'
        managed = False

class Sede(models.Model):
    house = models.CharField(max_length=255, blank=True, db_column='ramo')
    name = models.CharField(max_length=255, blank=True, db_column='denominazione')
#    legislatura = models.IntegerField(blank=True, null=True)
    site_type = models.CharField(max_length=255, blank=True, db_column='tipologia')
    code = models.CharField(max_length=255, blank=True, db_column='codice')
    start_date = models.DateField(blank=True, null=True, db_column='data_inizio')
    end_date = models.DateField(blank=True, null=True, db_column='data_fine')
    parlamento_id = models.IntegerField(blank=True, null=True)

    parliamentarians = models.ManyToManyField(Carica, through=CaricaInterna, related_name='sites')

    def __unicode__(self):
        if self.site_type.lower() in ['giunta', 'presidenza']:
            return u"{0.name} ({0.house})".format(self)
        else:
            return "{0.site_type} {0.name} ({0.house})".format(self)

    class Meta:
        db_table = 'opp_sede'
        managed = False


class PoliticianHistoryCache(models.Model):
#   legislatura = models.IntegerField(null=True, blank=True)
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
    charge = models.ForeignKey(Carica, blank=True, null=True,
                               db_column='chi_id',
                               related_name='+')
#    gruppo_id = models.IntegerField(null=True, blank=True)
    group = models.ForeignKey(Gruppo, null=True, blank=True,
                              db_column='gruppo_id',
                              related_name='charges+')
    house = models.CharField(max_length=1L, db_column='ramo')
    numero = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    @property
    def politico(self):
        return self.charge.politician


    def __unicode__(self):
        return self.politico.__unicode__()

    class Meta:
        db_table = 'opp_politician_history_cache'
        ordering = ('charge__politician__surname', 'charge__politician__name')
        managed = False


class Politico(models.Model):
    name = models.CharField(max_length=30L, blank=True, db_column='nome')
    surname = models.CharField(max_length=30L, blank=True, db_column='cognome')
    gender = models.CharField(max_length=1L, blank=True, db_column='sesso')
    monitoring_users = models.IntegerField(db_column='n_monitoring_users')

    def __unicode__(self):
        monitored_string = ""
        if self.gender == 'M':
            monitored_adj = "monitorato"
        else:
            monitored_adj = "monitorata"

        if self.monitoring_users:
            monitored_string= " - {1} da {0.monitoring_users} utenti".format(self, monitored_adj)
            if self.monitoring_users == 1:
                monitored_string = " - {0} da un utente".format(monitored_adj)

        return "{0.name} {0.surname}{1}".format(self, monitored_string)

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

    def dettagli(self):
        return self.votazionehascarica_set.values('vote', 'charge__politician', 'voting', 'rebel', 'maggioranza_sotto_salva')

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

    def __str__(self):
        return "vote: {0}, charge: {1}, voting: {2}".format(
            self.vote.titolo,
            self.charge.politician.name,
            self.voting
        )

    class Meta:
        db_table = 'opp_votazione_has_carica'
        managed = False

