# -*- coding: utf-8 -*-
__author__ = 'tommaso'

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





            locations_ids = OpInstitutionCharge.objects.using('politici').filter(
               # TODO: Remove limit
                institution_id=op_institution.id).values_list("location_id", flat=True).distinct()[0:20]

            for location_id in locations_ids:
                locations_names = OpLocation.objects.using('politici').filter(id=location_id)
                for location_name in locations_names:
                # create a new Organization only if not already imported
                    created = False
                    organization, created = Organization.objects.get_or_create(
                            identifiers__scheme='OPI',
                            identifiers__identifier="{0}:{1}".format(op_institution.id, location_id),

                            location_id = location_id,

                            defaults={
                                    'name' : op_institution.name,
                                    'location_name': location_name.name,


                                }
                            )

                    if created:
                        identifier = Identifier(identifier="{0}:{1}".format(op_institution.id, location_id),scheme="OPI")
                        organization.identifiers.add(identifier)
                        print organization, "created"
                    else:
                        organization.name = op_institution.name
                        organization.location_id = location_id
                        organization.location_name = location_name.name
                        organization.save()
                        print organization, "updated"


            op_posts = op_institution.charge_types.all()
            for op_post in op_posts:
                    post, created = Post.objects.get_or_create(
                        organization_id =organization.id,
                        label =op_post.name,
                        defaults={


                                    }
                                )














