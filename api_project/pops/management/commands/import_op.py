# -*- coding: utf-8 -*-
from optparse import make_option
import logging

from django.core.management.base import BaseCommand
from popolo.models import Membership

from pops.importers import OpImporter, OpImporterException
from politici.models import *

__author__ = 'guglielmo'


class Command(BaseCommand):
    """
    Data are imported from the Openpolis mysql database.

    If location ids are specified, then only those locations are imported.
    For each location, all institution charges, institutions and politicians are imported.

    OP database connection is named 'politici' and is accessible
    as a read-only database in django orm.
    """
    args = '<op_location_id op_location_id ...>'
    help = "Import data from old Openpolis database"

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

    logger = logging.getLogger('management')
    NATIONAL_INSTITUTIONS = (
        'governo nazionale',
        'camera dei deputati', 'senato della repubblica',
        'presidenza della repubblica',
        'commissariamento'
    )

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

        op_importer = OpImporter(logger=self.logger)

        if args:
            op_locs = OpLocation.objects.using('politici').filter(id__in=args)
        else:
            if limit:
                op_locs = OpLocation.objects.using('politici').all()[offset:offset+limit]
            else:
                op_locs = OpLocation.objects.using('politici').all()[offset:]

        for c, op_loc in enumerate(op_locs, start=offset):
            self.logger.info(
                "{0} - Processing {1} (op_location_id: {2})".format(
                    c, op_loc.name, op_loc.id
                )
            )
            area = op_importer.import_op_area(op_loc)

            op_charges = op_loc.opinstitutioncharge_set.all()
            for op_charge in op_charges:
                politician = op_importer.import_op_person(op_charge.politician)
                institution = op_importer.import_op_organization(op_charge.institution, area=area)
                post = op_importer.import_op_post(op_charge.charge_type, institution, area=area)

                # generate membership from post, person and organization
                membership = op_importer.import_op_membership(
                    op_charge,
                    post=post, organization=institution,
                    person=politician,
                    area=area
                )
