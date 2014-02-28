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
        make_option('--loc-type',
                    dest='loctype',
                    default='regione',
                    help='Type of location to import'),
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

    logger = logging.getLogger('management')



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
        loctype = options['loctype']

        offset = int(options['offset'])
        limit = int(options['limit'])

        self.logger.info("Inizio import da vecchio DB")
        self.logger.info("Tipo territorio: %s" % loctype)
        self.logger.info("Limit: %s" % limit)
        self.logger.info("Offset: %s" % offset)


        if limit:
            op_locations = OpLocation.objects.using('politici').filter(
                location_type__name__iexact=loctype
            )[offset:offset+limit]
        else:
            op_locations = OpLocation.objects.using('politici').filter(
                location_type__name__iexact=loctype
            )[offset:]

        if args:
            op_locations = op_locations.filter(city_id__in=args)

        self._prepare_classification()

        c = offset
        for op_location in op_locations:

            # increment counter, to be shown in import log
            c += 1

            #
            # Place Type
            #

            op_location_type_name = op_location.location_type.name
            if op_location_type_name == 'Europa':
                op_location_type_name = 'Continent'
            elif op_location_type_name == 'Italia':
                op_location_type_name = 'Nation'

            place_type, created = PlaceType.objects.get_or_create(
                name=op_location_type_name
            )
            if created:
                self.logger.info(u"%s - New place type added: %s" % (c, place_type))

            #
            # Place
            #

            slug = slugify(u"{0}-{1}".format(op_location.name, place_type.name))
            if op_location_type_name.lower() == 'comune':
                slug = "{0}-{1}".format(slug, op_location.prov.lower())

            created = False
            place, created = Place.objects.get_or_create(
                slug=slug,
                defaults={
                    'place_type': place_type,
                    'name': op_location.name,
                    'inhabitants': op_location.inhabitants,
                    'start_date': op_location.date_start,
                    'end_date': op_location.date_end,
                    'slug': slug,
                }
            )
            if created:
                self.logger.info(
                    u"{0} - New place added: {1} ({2})".format(
                        c, place, slug
                    )
                )
            else:
                place.place_type = place_type
                place.name = op_location.name
                place.inhabitants_total = op_location.inhabitants
                place.start_date = op_location.date_start
                place.end_date = op_location.date_end
                place.slug = slug
                place.save()
                self.logger.info(
                    u"{0} - Place found and modified: {1} ({2})".format(
                        c, place, slug
                    )
                )

            # add external identifiers
            self._add_external_identifiers(place, op_location)

            # lat and long
            geoinfo, created = PlaceGEOInfo.objects.get_or_create(place=place)
            if op_location.gps_lat or op_location.gps_lon:
                geoinfo.gps_lat = op_location.gps_lat
                geoinfo.gps_lon = op_location.gps_lon
                geoinfo.save()
                self.logger.debug(u"  lat and long added in geoinfo")


            # ISTAT_REG classification
            self._add_istat_classification(place, op_location)

        self.logger.info("Fine")


    def _add_external_identifiers(self, place, op_location):

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



    def _prepare_classification(self):
        # preparatory work
        # get or create istat tag
        tag, created = ClassificationTreeTag.objects.get_or_create(
            slug='istat-reg',
            defaults={
                'label': 'ISTAT-REG',
                'description': \
                    "ISTAT classification for administrative " +\
                    "entities in Italy: Regioni, Province, Comuni"
            }
        )
        if created:
            self.logger.info("Classification Tag created: {0}".format(
                tag
            ))
        else:
            self.logger.debug("Classification Tag found: {0}".format(
                tag
            ))


        # get or create root node
        root_tag, created = ClassificationTreeTag.objects.get_or_create(
            slug='root',
            defaults={
                'label': 'ROOT',
            }
        )
        root_node, created = ClassificationTreeNode.objects.get_or_create(
            tag=root_tag,
            place=None,
            parent=None
        )
        if created:
            self.logger.info("Root ClassificationNode created")
        else:
            self.logger.debug("Root ClassificationNode found")

        self.tag = tag
        self.root_tag = root_tag
        self.root_node = root_node


    def _add_istat_classification(self, place, op_location):

        if op_location.location_type.pk == 2:

            # get or create europe node
            eu_node, created = ClassificationTreeNode.objects.get_or_create(
                tag=self.tag,
                place=place,
                parent=self.root_node,
            )
            if created:
                self.logger.info("Europe ClassificationNode created")
            else:
                self.logger.info("Europe ClassificationNode found")


        if op_location.location_type.pk == 3:

            # get or create italy node
            parent_node = Place.objects.get(slug='europa-continent').referencing_nodes('istat-reg')[0]
            it_node, created = ClassificationTreeNode.objects.get_or_create(
                tag=self.tag,
                place=place,
                parent=parent_node,
            )
            if created:
                self.logger.info("Italy ClassificationNode created")
            else:
                self.logger.info("Italy ClassificationNode found")


        if op_location.location_type.pk == 4:

            # get or create region node
            parent_node = Place.objects.get(slug='italia-nation').referencing_nodes('istat-reg')[0]
            node, created = ClassificationTreeNode.objects.get_or_create(
                tag=self.tag,
                place=place,
                parent=parent_node,
            )
            if created:
                self.logger.info(u"Region {0} ClassificationNode created".format(
                    place.name
                ))
            else:
                self.logger.info(u"Regione {0} ClassificationNode found".format(
                    place.name
                ))


        if op_location.location_type.pk == 5:

            # get or create province node
            parent_place = Place.objects.get(
                place_type__name='Regione',
                placeidentifiers__identifier__scheme='ISTAT',
                placeidentifiers__identifier__name='REGION_ID',
                placeidentifiers__value=op_location.regional_id,
            )
            parent_node = parent_place.referencing_nodes('istat-reg')[0]

            prov_node, created = ClassificationTreeNode.objects.get_or_create(
                tag=self.tag,
                place=place,
                parent=parent_node,
            )
            if created:
                self.logger.info(u"Provincia di {0} ClassificationNode created".format(
                    place.name
                ))
            else:
                self.logger.info(u"Provincia di {0} ClassificationNode found".format(
                    place.name
                ))


        if op_location.location_type.pk == 6:

            # get or create city node
            parent_place = Place.objects.get(
                place_type__name='Provincia',
                placeidentifiers__identifier__scheme='ISTAT',
                placeidentifiers__identifier__name='PROVINCE_ID',
                placeidentifiers__value=op_location.provincial_id,
            )
            parent_node = parent_place.referencing_nodes('istat-reg')[0]

            node, created = ClassificationTreeNode.objects.get_or_create(
                tag=self.tag,
                place=place,
                parent=parent_node,
            )
            if created:
                self.logger.info(u"Comune di {0} ClassificationNode created".format(
                    place.name
                ))
            else:
                self.logger.info(u"Comune di {0} ClassificationNode found".format(
                    place.name
                ))

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
            self.logger.info(u"   - New identifier added: %s" % (identifier))
        else:
            self.logger.debug(u"   - Identifier found: %s" % (identifier))

        extid, created = place.placeidentifiers.get_or_create(
            identifier=identifier,
            defaults={
                'value': kwargs['value'],
            }
        )
        if created is True:
            self.logger.debug(u"   - Id {0} added".format(extid,))
        else:
            extid.value = kwargs['value']
            extid.save()
            self.logger.debug(u"   - Id {0} overwritten".format(extid,))

