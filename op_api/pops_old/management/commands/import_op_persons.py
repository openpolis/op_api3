# -*- coding: utf-8 -*-
__author__ = 'guglielmo'

from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from politici.models import *
from op_api.pops.models import *


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
        for op_person in op_politicians:

            # increment counter, to be shown in import log
            c += 1

            if op_person.sex:
                if op_person.sex == 'M':
                    op_person_sex = Person.SEX.male
                else:
                    op_person_sex = Person.SEX.female

            #
            # Contacts
            #
            op_resources = op_person.opresources_set.all()
            contacts = []
            if op_resources:
                for op_resource in op_resources:
                    created = False
                    contact_type, created = ContactType.objects.get_or_create(
                        name=op_resource.resources_type.denominazione
                    )
                    if created:
                        self.logger.info(u"%s - Aggiunto nuovo contact type: %s" % (c, contact_type))

                    created = False
                    contact, created = Contact.objects.get_or_create(
                        description=op_resource.descrizione,
                        value=op_resource.valore,
                        contact_type=contact_type,
                    )
                    if created:
                        self.logger.info(u"%s - Aggiunto nuovo contact: %s" % (c, contact))

                    contacts.append(contact)

            #
            # Profession
            #

            # profession is created only if non-existing
            profession = None
            created = False
            if op_person.profession is not None:
                profession, created = Profession.objects.get_or_create(
                    name=op_person.profession.description,
                )
                if created:
                    self.logger.info(u"%s - Aggiunta professione: %s" % (c, profession))
                    # check if the profession is a sub-division of an original profession (OP)
                    # in case, get_or_create the original profession, as main record of the UnifiedModel
                    if op_person.profession.oid is not None:
                        op_original_prof = OpProfession.objects.using('politici').get(pk=op_person.profession.oid)
                        mpc = False
                        main_profession, mpc = Profession.objects.get_or_create(
                            name=op_original_prof.description,
                        )
                        if mpc:
                            self.logger.info(u"%s - Aggiunta professione main: %s" % (c, main_profession))
                        profession.main = main_profession
                        profession.save()

            #
            # Education Levels
            #

            # extract all OP education levels for the politician
            op_education_levels = [el.education_level for el in op_person.oppoliticianhasopeducationlevel_set.all()]

            # build the education_levels in the new DB, creating sub-instances and main instances if non-existing
            education_levels = []
            if op_education_levels:
                for op_education_level in op_education_levels:

                    # new EducationLevel record is created only if non-extisting
                    created = False
                    education_level, created = EducationLevel.objects.get_or_create(
                        name=op_education_level.description,
                    )
                    if created:
                        self.logger.info(u"%s - Aggiunto livello educativo: %s" % (c, education_level))
                        # check if the education level is a sub-division of an original one (UnifiedModel)
                        if op_education_level.oid is not None:
                            op_original_education_level = OpEducationLevel.objects.using('politici').\
                                get(pk=op_education_level.oid)
                            main_education_level, mel = EducationLevel.objects.get_or_create(
                                name=op_original_education_level.description,
                            )
                            if mel:
                                self.logger.info(u"%s - Aggiunto livello educativo main: %s" % (c, main_education_level))

                            education_level.main = main_education_level
                            education_level.save()
                    education_levels.append(education_level)

            #
            # Person
            #

            # create a new Person only if not already imported
            created = False
            person, created = Person.objects.get_or_create(
                code__name='op_id',
                code__code=op_person.content_id,
                defaults={
                    'first_name': op_person.first_name,
                    'last_name': op_person.last_name,
                    'birth_date': op_person.birth_date,
                    'sex': op_person_sex if op_person_sex else None,
                }
            )
            if created:
                code = Code.objects.create(name='op_id', code=op_person.content_id, person=person)
                self.logger.info(u"%s - Aggiunta persona: %s" % (c, person))

                # add related data
                if contacts:
                    for contact in contacts:
                        person.contact_set.add(contact)
                        self.logger.info(u"    |- aggiunto contatto %s alla persona" % contact)
                if profession:
                    pp = PersonHasProfession.objects.create(
                        person=person, profession=profession,
                    )
                    pp.save()
                    self.logger.info(u"    |- aggiunta professione %s alla persona" % profession)
                if education_levels:
                    for education_level in education_levels:
                        pe = PersonHasEducationLevel.objects.create(
                            person=person, education_level=education_level
                        )
                        pe.save()
                        self.logger.info(u"    |- aggiunto livello educazione %s alla persona" % education_level)
            else:
                self.logger.debug(u"%s - Trovata persona: %s" % (c, person))
                # overwrite if required by the script
                if overwrite:
                    # overwrite main metadata
                    person.first_name = op_person.first_name
                    person.last_name = op_person.last_name
                    person.birth_date = op_person.birth_date
                    person.sex = op_person_sex if op_person_sex else None
                    self.logger.debug(u"    |- dati anagrafici sovrascritti")

                    # overwrite related data
                    if contacts:
                        person.contact_set.all().delete()
                        self.logger.debug(u"    |- contatti rimossi")
                        for contact in contacts:
                            person.contact_set.add(contact)
                            self.logger.info(u"    |- aggiunto contatto %s alla persona" % contact)

                    if profession:
                        person.personhasprofession_set.all().delete()
                        self.logger.debug(u"    |- professioni rimosse")
                        pp = PersonHasProfession.objects.create(
                            person=person, profession=profession,
                        )
                        pp.save()
                        self.logger.debug(u"    |- aggiunta professione %s" % profession)

                    if education_levels:
                        person.personhaseducationlevel_set.all().delete()
                        self.logger.debug(u"    |- livelli educativi rimossi")
                        for education_level in education_levels:
                            pe = PersonHasEducationLevel.objects.create(
                                person=person, education_level=education_level
                            )
                            pe.save()
                            self.logger.debug(u"    |- aggiunto livello educazione %s alla persona" % education_level)

                    # persiste changes to person
                    person.save()


        self.logger.info("Inizio import da vecchio DB")
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        self.logger.info("Fine")






