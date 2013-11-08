# -*- coding: utf-8 -*-
__author__ = 'guglielmo'

from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from op_api.politici.models import *
from popolo.models import *


class Command(BaseCommand):
    """
    Politici are imported from the old Openpolis database into the new one

    Old database connection is named 'politici' and is accessible as a read-only
    database in django orm.
    """
    help = "Import persons data from old Organization database"

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

        if limit:
            op_institutions = OpInstitution.objects.using('politici').all()[offset:offset+limit]
        else:
            op_institutions = OpInstitution.objects.using('politici').all()[offset:]

        c = offset
        i=0
        for op_institution in op_institutions:

            c += 1




            o = Organization()



            # create a new Person only if not already imported
            created = False
            organization, created = Organization.objects.get_or_create(
                identifiers__scheme='OPI',
                identifiers__identifier=op_institution.id,
                defaults={
                    'name': op_institution.name,

                }
            )

            if created:
                identifier = Identifier(identifier=op_institution.id,scheme='OPI')
                organization.identifiers.add(identifier)

                print organization, "created"
            else:
                organization.name = op_institution.name

                organization.save()
                print organization, "updated"


        self.logger.info("Inizio import da vecchio DB")
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        self.logger.info("Fine")
