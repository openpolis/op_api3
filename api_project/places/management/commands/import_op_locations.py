# -*- coding: utf-8 -*-
from django.utils.text import slugify

__author__ = 'guglielmo'

from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from places.models import *
from territori.models import *


class Command(BaseCommand):
    """
    Places are imported from the old Openpolis OpLocation table

    Old database connection is named 'politici' and is accessible as a read-only
    database in django orm.
    """
    help = "Import places data from old politici database"

    option_list = BaseCommand.option_list + (
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to start from'),
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual import is made'),
        make_option('--overwrite',
                    dest='overwrite',
                    default=False,
                    action='store_true',
                    help='Always overwrite values in the new DB from values in the old one'),
        )

    logger = logging.getLogger('import')


    def _create_or_update_identifier(self, place, **kwargs):
        """
        Associate an external identifier to a given place.
        Needed parameters for kwargs:

        - scheme
        - name
        - value

        New identifiers are created, old ones overwritten.
        """
        if kwargs['name'] is None:
            return

        if kwargs['value'] is None:
            return

        identifier, created = Identifier.objects.get_or_create(
            scheme=kwargs['scheme'],
            name=kwargs['name'],
        )

        if created is True:
            self.logger.info(u"  - New identifier added: %s" % (identifier))
        else:
            self.logger.debug(u"  - Identifier found: %s" % (identifier))

        extid, created = place.placeidentifier_set.get_or_create(
            identifier=identifier,
            defaults={
                'value': kwargs['value'],
            }
        )
        if created is True:
            self.logger.debug(u"External id {0} added".format(extid,))
        else:
            extid.value = kwargs['value']
            extid.save()
            self.logger.debug(u"External id {0} overwritten".format(extid,))


    def handle(self, *args, **options):

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        dryrun = options['dryrun']
        overwrite = options['overwrite']

        offset = int(options['offset'])
        limit = int(options['limit'])

        self.logger.info("Inizio import da vecchio DB")
        self.logger.info("Limit: %s" % limit)
        self.logger.info("Offset: %s" % offset)


        if limit:
            op_locations = OpLocation.objects.using('politici').all()[offset:offset+limit]
        else:
            op_locations = OpLocation.objects.using('politici').all()[offset:]


        c = offset
        for op_location in op_locations:

            # increment counter, to be shown in import log
            c += 1

            #
            # Place Type
            #

            # TODO: map italian names into standard english names
            # TODO: Europa => Continent, Italia => Nation/Country, ...
            op_location_type = op_location.location_type
            place_type, created = PlaceType.objects.get_or_create(
                name=op_location_type.name
            )
            if created:
                self.logger.info(u"%s - New place type added: %s" % (c, place_type))

            #
            # Place
            #
            slug = slugify(u"{0}-{1}".format(op_location.name, place_type.name))
            self.logger.debug(u"slug built: {0}".format(slug))

            created = False
            place, created = Place.objects.get_or_create(
                slug=slug,
                defaults={
                    'place_type': place_type,
                    'name': op_location.name,
                    'inhabitants': op_location.inhabitants,
                    'start_date': op_location.date_start,
                    'end_date': op_location.date_end,
                }
            )
            if created:
                self.logger.info(u"%s - New place added: %s" % (c, place))
            else:
                place.place_type = place_type
                place.name = op_location.name
                place.inhabitants_total = op_location.inhabitants
                place.start_date = op_location.date_start
                place.end_date = op_location.date_end
                place.save()
                self.logger.debug(u"%s - Place found and modified: %s" % (c, place))

            # OP Identifiers associated with the place
            self._create_or_update_identifier(
                place, scheme='ISTAT', name='MACROREGION_ID',
                value=op_location.macroregional_id
            )
            self._create_or_update_identifier(
                place, scheme='ISTAT', name='REGION_ID',
                value=op_location.regional_id
            )
            self._create_or_update_identifier(
                place, scheme='ISTAT', name='PROVINCE_ID',
                value=op_location.provincial_id
            )
            self._create_or_update_identifier(
                place, scheme='ISTAT', name='CITY_ID',
                value=op_location.city_id
            )
            self._create_or_update_identifier(
                place, scheme='MININT', name='REGION_ID',
                value=op_location.minint_regional_code
            )
            self._create_or_update_identifier(
                place, scheme='MININT', name='PROVINCE_ID',
                value=op_location.minint_provincial_code
            )
            self._create_or_update_identifier(
                place, scheme='MININT', name='CITY_ID',
                value=op_location.minint_city_code
            )
            self._create_or_update_identifier(
                place, scheme='OP', name='LOCATION_ID',
                value=op_location.pk
            )

            # lat and long
            if op_location.gps_lat or op_location.gps_lon:
                geoinfo, created = PlaceGEOInfo.objects.get_or_create(place=place)
                geoinfo.gps_lat = op_location.gps_lat
                geoinfo.gps_lon = op_location.gps_lon
                geoinfo.save()
                self.logger.debug(u"  lat and long added in geoinfo")


        self.logger.info("Fine")






