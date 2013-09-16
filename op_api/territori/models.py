# -*- coding: utf-8 -*-
from django.db import models

# edit to load from other database
DBNAME = 'politici'


class OpLocationType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=96)
    class Meta:
        db_table = u'op_location_type'
        managed = False
    def __unicode__(self):
        return self.name


class OpLocationQuerySet(models.query.QuerySet):

    _cache = {}
    def _location_query(self, method, key, key_field='pk'):
        """ returns a get cached query"""
        cache_key = "%s_by_%s_%s" % (method, key_field, key)
        if cache_key not in OpLocationQuerySet._cache:
            OpLocationQuerySet._cache[cache_key] = getattr(self, method)().get(**{key_field:key})
        return OpLocationQuerySet._cache[cache_key]


    def regioni(self):
        return self.filter(location_type_id=OpLocation.REGION_TYPE_ID)

    def regione(self, id, codename='op'):
        try:
            return getattr(self, {
                                     'op': 'regione_from_id',
                                     'istat': 'regione_from_istat_id',
                                     }[codename])( id )
        except KeyError:
            raise Exception("'%s' is invalid codename for location" % codename)


    def regione_from_location(self, comune_or_provincia):
        """return an Location object that contains provided location"""
        return self._location_query('regioni', comune_or_provincia.regional_id, 'regional_id')

    def regione_from_id(self, id):
        """return an Location region object from primary key"""
        return self._location_query('regioni', id)

    def regione_from_istat_id(self, id):
        """return an Location region object, from the istat regional_id"""
        return self.regioni().get(regional_id = id )

    def province(self):
        return self.filter(location_type_id=OpLocation.PROVINCE_TYPE_ID)

    def provincia(self, id, codename='op'):
        try:
            return getattr(self, {
                                     'op': 'provincia_from_id',
                                     'istat': 'provincia_from_istat_id',
                                     }[codename])( id )
        except KeyError:
            raise Exception("'%s' is invalid codename for location" % codename)

    def provincia_from_location(self, comune):
        """return an Location object that contains provided location"""
        return self._location_query('province', comune.provincial_id, 'provincial_id')

    def provincia_from_id(self, id):
        """return an Location province object from primary key"""
        return self._location_query('province', id)

    def provincia_from_istat_id(self, id):
        """return an Location object, from the istat provincial_id"""
        return self._location_query('province', id, 'provincial_id')

    def comuni(self):
        return self.filter(location_type_id=OpLocation.CITY_TYPE_ID)

    def comune_from_id(self, id):
        """return an Location city object from primary key"""
        return self._location_query('comuni', id)

    def comune_from_istat_id(self, id):
        """return an Location object, from the istat city_id"""
        return self._location_query('comuni', id, 'city_id')

    def comune_from_minint_id(self, minint_id):
        """
        return an Location object, from the minint codes
        minint codes is packed: 2A3A4A
        the argument length is validated
        codes are unpacked from the argument
        """
        if len(minint_id) != 9:
            raise Exception('minint_id code must be exactly 9 characters long: %s is %s char-long' % (id, len(minint_id),))
        regional_code = int(id[:2])
        provincial_code = int(id[2:5])
        city_code = int(id[5:])

        return self.comuni().get(minint_regional_code=regional_code,
                                 minint_provincial_code=provincial_code,
                                 minint_city_code=city_code)

    def comune(self, id, codename='op'):
        try:
            return getattr(self, {
                                     'op': 'comune_from_id',
                                     'istat': 'comune_from_istat_id',
                                     'minint': 'comune_from_minint_id'
                                 }[codename])( id )
        except KeyError:
            raise Exception("'%s' is invalid codename for location" % codename)



class OpLocationManager(models.Manager):

    def get_query_set(self):
        return OpLocationQuerySet(self.model, using=self._db)

    def regioni(self): return self.get_query_set().regioni()
    def regione(self, territorio, codename='op'): return self.get_query_set().regione(territorio, codename)
    def regione_from_id(self, id): return self.regione(id, codename='op')
    def regione_from_istat_id(self, id): return self.regione(id, codename='istat')
    def province(self): return self.get_query_set().province()
    def provincia(self, territorio, codename='op'): return self.get_query_set().provincia(territorio, codename)
    def provincia_from_id(self, id): return self.provincia(id, codename='op')
    def provincia_from_istat_id(self, id): return self.provincia(id, codename='istat')
    def comuni(self): return self.get_query_set().comuni()
    def comune(self, territorio_id, codename='op'): return self.get_query_set().comune(territorio_id, codename=codename)
    def comune_from_id(self, id): return self.comune(id, codename='op')
    def comune_from_istat_id(self, id): return self.comune(id, codename='istat')
    def comune_from_minint_id(self, id): return self.comune(id, codename='minint')

    def retrieve_by_type(self, location_type, location_id, codename='op'):
        if isinstance(location_type, (int,long)):
            if location_type == OpLocation.CITY_TYPE_ID:
                return self.comune(location_id, codename=codename)
            if location_type == OpLocation.PROVINCE_TYPE_ID:
                return self.comune(location_id, codename=codename)
            if location_type == OpLocation.REGION_TYPE_ID:
                return self.regione(location_id, codename=codename)
        else:
            if location_type == 'regional':
                return self.regione(location_id, codename=codename)
            if location_type == 'provincial':
                return self.provincia(location_id, codename=codename)
            elif location_type == 'city':
                return self.comune(location_id, codename=codename)

        raise Exception('wrong location_type parameters %s not in (regional, provincial, city)' % location_type)



class OpLocation(models.Model):

    CITY_TYPE_ID = 6
    PROVINCE_TYPE_ID = 5
    REGION_TYPE_ID = 4

    id = models.IntegerField(primary_key=True)
    location_type = models.ForeignKey(OpLocationType)
    name = models.CharField(max_length=255, blank=True)
    macroregional_id = models.IntegerField(null=True, blank=True)
    regional_id = models.IntegerField(null=True, blank=True)
    provincial_id = models.IntegerField(null=True, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    prov = models.CharField(max_length=2, blank=True, null=True)
    inhabitants = models.IntegerField(null=True, blank=True)
    last_charge_update = models.DateTimeField(null=True, blank=True)
    alternative_name = models.CharField(max_length=255, blank=True, null=True)
    minint_regional_code = models.IntegerField(null=True, blank=True)
    minint_provincial_code = models.IntegerField(null=True, blank=True)
    minint_city_code = models.IntegerField(null=True, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    new_location_id = models.IntegerField(null=True, blank=True)
    gps_lat = models.FloatField(null=True, blank=True)
    gps_lon = models.FloatField(null=True, blank=True)

    objects = OpLocationManager()

    class Meta:
        db_table = u'op_location'
        managed = False

    def __unicode__(self):
        bits = [self.name]
        if self.location_type_id == OpLocation.CITY_TYPE_ID:
            bits.insert(0,u'Comune di')
            bits.append(u'(%s)' % self.prov)
        elif self.location_type_id == OpLocation.PROVINCE_TYPE_ID:
            bits.insert(0,u'Provincia di')
        elif self.location_type_id == OpLocation.REGION_TYPE_ID:
            bits.insert(0,u'Regione')

        return u" ".join(bits)

    @property
    def minint_id(self):
        """
        regional_code = int(minint_id[:2])
        provincial_code = int(minint_id[2:5])
        city_code = int(minint_id[5:])
        """
        return "{0}{1}{2}".format(
            str(self.minint_regional_code).zfill(2),
            str(self.minint_provincial_code).zfill(3),
            str(self.minint_city_code).zfill(4)
        )


    def getProvince(self):
        if self.location_type_id != OpLocation.CITY_TYPE_ID:
            raise Exception("This method can be called only for cities")
        return OpLocation.objects.using(DBNAME).provincia_from_location( self )


    def getRegion(self):
        if self.location_type_id not in (OpLocation.CITY_TYPE_ID, OpLocation.PROVINCE_TYPE_ID):
            raise Exception("This method can be called only for cities or provinces")
        return OpLocation.objects.using(DBNAME).regione_from_location( self )


    def getConstituencies(self, election_type=None, prov_id=None):
        """docstring for getConstituency"""
        from op_api.politici.models import OpConstituency

        if prov_id is None:
            prov_id = self.getProvince().id

        kwargs = {
            'opconstituencylocation__location_id': prov_id
        }
        if election_type:
            if isinstance(election_type, (int,long)):
                kwargs['election_type__id']= election_type
            else:
                kwargs['election_type__name']= election_type
        return OpConstituency.objects.db_manager(DBNAME).filter(**kwargs)

    def getConstituency(self, election_type, prov_id=None):
        from op_api.politici.models import OpConstituency

        try:
            return self.getConstituencies(election_type, prov_id)[0]
        except IndexError:
            raise OpConstituency.DoesNotExist

    def getNationalReps(self, election_type, prov_id=None):
        """docstring for getNationalReps"""
        from op_api.politici.models import OpInstitutionCharge

        constituency = self.getConstituency(election_type, prov_id)
        charges = OpInstitutionCharge.objects.db_manager(DBNAME).filter(
            date_end=None,
            constituency__id=constituency.id,
            content__deleted_at=None
        ).order_by('politician__last_name')
        reps = []
        for charge in charges:
            reps.append({
                'first_name': charge.politician.first_name,
                'last_name': charge.politician.last_name,
                'charge': charge.charge_type.name,
                'charge_id': charge.content_id,
                'politician_id': charge.politician.content_id,
                })
        return {
            'constituency': constituency.name,
            'representatives': reps
        }

    def getLocalReps(self, institution_name):
        """docstring for getLocalReps"""
        from op_api.politici.models import OpInstitutionCharge

        charges = OpInstitutionCharge.objects.db_manager(DBNAME).filter(
            institution__name=institution_name,
            location__id=self.id,
            date_end=None,
            content__deleted_at=None,
            ).order_by('charge_type__priority', 'politician__last_name')
        reps  = []

        for charge in charges:
            reps.append({
                'first_name': charge.politician.first_name,
                'last_name': charge.politician.last_name,
                'charge': charge.charge_type.name,
                'charge_id': charge.content_id,
                'politician_id': charge.politician.content_id,
                })
        return reps