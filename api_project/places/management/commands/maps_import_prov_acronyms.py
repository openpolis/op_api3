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
    Province acronyms are  imported from the old Openpolis OpLocation table

    Old database connection is named 'politici' and is accessible as a read-only
    database in django orm.
    """
    help = "Import provinces acronyms from old politici database"

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual import is made'),
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

        self.logger.info("Inizio import acronimi province")


        op_locations = OpLocation.objects.using('politici').filter(
            location_type__name__iexact='provincia'
        )

        if args:
            op_locations = op_locations.filter(city_id__in=args)

        c = 0
        for op_location in op_locations:

            # increment counter, to be shown in import log
            c += 1

            #
            # Place
            #

            slug = slugify(u"{0}-{1}".format(op_location.name, 'provincia'))
            place = Place.objects.get(slug=slug)
            if not dryrun:
                try:
                    self.logger.info(
                        u"{0} - Adding acronym {1} to place {2}".format(
                            c, op_location.prov, place
                        )
                    )
                    PlaceAcronym.objects.create(place=place, acronym=op_location.prov)
                except Exception, e:
                    self.logger.warning(
                        u"Error: {0}. Skipping insertion".format(e)
                    )

            else:
                    self.logger.info(
                        u"{0} - Acronym {1} will be added to place {2}".format(
                            c, op_location.prov, place
                        )
                    )


