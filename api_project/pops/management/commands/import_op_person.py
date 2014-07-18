# -*- coding: utf-8 -*-
__author__ = 'guglielmo'

from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from politici.models import *
from popolo.models import *
import re

class Command(BaseCommand):
    """
    Politici are imported from the old Openpolis database into the new one

    Old database connection is named 'politici' and is accessible as a read-only
    database in django orm.
    """
    help = "Import persons data from old politici database"

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
            op_politicians = OpPolitician.objects.using('politici').all()[offset:offset+limit]
        else:
            op_politicians = OpPolitician.objects.using('politici').all()[offset:]

        c = offset
        i=0
        resources_type_map = {
            1 : ContactDetail.CONTACT_TYPES.email,
            2 : ContactDetail.CONTACT_TYPES.email,
            5 : ContactDetail.CONTACT_TYPES.twitter,
            6 : ContactDetail.CONTACT_TYPES.facebook,
        }
        for op_person in op_politicians:

            op_id = op_person.content_id
            c += 1
            p = Person()

            gender = None
            if op_person.sex:
                gender = op_person.sex

            birth_date = op_person.birth_date.strftime('%Y-%m-%d')

            death_date = ''
            if op_person.death_date:
                death_date = op_person.death_date.strftime('%Y-%m-%d')

            # create a new Person only if not already imported
            created = False
            person, created = Person.objects.get_or_create(
                identifiers__scheme='OP',
                identifiers__identifier=op_person.content_id,
                defaults={
                    'name': u"{0} {1}".format(op_person.first_name.lower().capitalize(), op_person.last_name.lower().capitalize()),
                    'first_name': op_person.first_name,
                    'family_name': op_person.last_name,
                    'birth_date': birth_date,
                    'death_date': death_date,
                    'gender': gender,
                }
            )

            if created:
                identifier = Identifier(identifier=op_person.content_id,scheme='OP')
                person.identifiers.add(identifier)

                print person,  "created"
            else:
                person.name = u"{0} {1}".format(op_person.first_name.lower().capitalize(), op_person.last_name.lower().capitalize())
                person.first_name = op_person.first_name
                person.family_name = op_person.last_name
                person.birth_date = birth_date
                person.death_date = death_date
                person.gender = gender
                person.save()
                print person, "updated"


            op_person_resources = OpResources.objects.using('politici').filter(
                politician_id=op_id,resources_type_id__in=(1,2,5,6))

            for op_resource in op_person_resources:
                contact, created = ContactDetail.objects.get_or_create(
                    contact_type=resources_type_map[op_resource.resources_type_id],
                    value=op_resource.valore,
                    content_type=ContentType.objects.get(model='person', app_label='popolo'),
                    object_id=person.id,
                    defaults={
                        'label':op_resource.descrizione
                    }
                )


        self.logger.info("Inizio import da vecchio DB")
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        self.logger.info("Fine")
