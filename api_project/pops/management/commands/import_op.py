# -*- coding: utf-8 -*-
from optparse import make_option
import logging
from itertools import tee, islice, izip_longest
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand
from django.db.models import Q
from popolo.models import Membership, Organization

from pops.importers import OpImporter, OpImporterException
from politici.models import *


__author__ = 'guglielmo'


def get_next(some_iterable, window=1):
    """
    returns an iterable that pre-fetches next item
    usage:
        for line, next_line in get_next(original_iterable):
            ... do stuff

    :param   some_iterable: the original iterable
    :param   window: the number of lines to look ahead
    :return: iterable of tuples
    """
    items, nexts = tee(some_iterable, 2)
    nexts = islice(nexts, window, None)
    return izip_longest(items, nexts)



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

            op_charges = op_loc.opinstitutioncharge_set.filter(
                content__deleted_at__isnull=True
            ).order_by('date_start')

            apical_q = (
                Q(charge_type__name__iexact='sindaco') |
                Q(charge_type__name__iexact='presidente') & Q(institution__name__iexact='giunta provinciale') |
                Q(charge_type__name__iexact='presidente') & Q(institution__name__iexact='giunta regionale')
            )

            op_apical_charges = op_charges.filter(apical_q)
            for op_charge, op_next_charge in get_next(op_apical_charges):
                #
                # build institution hierarchy, with founding and dissolution dates
                # corresponding to apical charge start and end dates
                #

                # a generic time-independent organization for the institution
                institution, created = Organization.objects.get_or_create(
                    classification=op_loc.location_type.name,
                    area=area,
                    defaults={
                        'name' : op_importer.get_full_location_name(op_loc),
                    }
                )

                if op_next_charge:
                    dissolution_date = op_next_charge.date_start
                else:
                    dissolution_date = None

                # the government institution (giunta)
                classification = op_charge.institution.name
                institution_name = op_importer.get_full_institution_name(classification, area.name, op_charge.date_start)
                gov_institution, created = Organization.objects.get_or_create(
                    classification=classification,
                    area=area,
                    founding_date=op_charge.date_start,
                    dissolution_date=dissolution_date,
                    defaults={
                        'name' : institution_name,
                        'parent_id': institution.id
                    }
                )

                # the corresponding council institution
                classification = op_charge.institution.name.replace('Giunta', 'Consiglio')
                institution_name = op_importer.get_full_institution_name(classification, area.name, op_charge.date_start)
                cou_institution, created = Organization.objects.get_or_create(
                    classification=classification,
                    area=area,
                    founding_date=op_charge.date_start,
                    dissolution_date=dissolution_date,
                    defaults={
                        'name' : institution_name,
                        'parent': institution
                    }
                )


                politician = op_importer.import_op_person(op_charge.politician)
                gov_membership = op_importer.import_op_membership(
                    op_charge,
                    organization=gov_institution,
                    person=politician,
                    area=area
                )
                cou_membership = op_importer.import_op_membership(
                    op_charge,
                    organization=cou_institution,
                    person=politician,
                    area=area
                )


            # the generic government institution (giunta), with no dates
            classification = op_charge.institution.name
            institution_name = u"{0} - legislatura non specificata".format(
                op_importer.get_full_institution_name(classification, area.name)
            )
            gov_institution, created = Organization.objects.get_or_create(
                classification=classification,
                area=area,
                founding_date=None,
                defaults={
                    'name' : institution_name,
                    'parent_id': institution.id
                }
            )

            # the corresponding council institution
            classification = op_charge.institution.name.replace('Giunta', 'Consiglio')
            institution_name = u"{0} - legislatura non specificata".format(
                op_importer.get_full_institution_name(classification, area.name)
            )
            cou_institution, created = Organization.objects.get_or_create(
                classification=classification,
                area=area,
                founding_date=None,
                defaults={
                    'name' : institution_name,
                    'parent': institution
                }
            )

            op_normal_charges = op_charges.exclude(apical_q)
            for op_charge in op_normal_charges:
                institutions = Organization.objects.filter(
                    area=area,
                    classification = op_charge.institution.name,
                    founding_date__lte=op_charge.date_start,
                ).order_by('founding_date')
                if institutions.count() > 0:
                    institution = institutions[0]
                else:
                    institution = Organization.objects.get(
                        area=area,
                        classification=op_charge.institution.name,
                        founding_date=None
                    )

                politician = op_importer.import_op_person(op_charge.politician)
                membership = op_importer.import_op_membership(
                    op_charge,
                    organization=institution,
                    person=politician,
                    area=area
                )
