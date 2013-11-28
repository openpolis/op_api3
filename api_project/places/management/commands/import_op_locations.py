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
            # Place Types
            #

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
                place.save()
                self.logger.debug(u"%s - Place found and modified: %s" % (c, place))

        self.logger.info("Fine")






