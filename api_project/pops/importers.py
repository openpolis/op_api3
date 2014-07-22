import logging
from django.contrib.contenttypes.models import ContentType
from politici.models import OpResources
from popolo.models import Identifier, Area, ContactDetail, Person, Link, Source

__author__ = 'guglielmo'


class OpImporter(object):
    logger = logging.getLogger('console')

    RESOURCES_TYPE_MAP = {
        1 : ContactDetail.CONTACT_TYPES.email,
        2 : ContactDetail.CONTACT_TYPES.email,
        5 : ContactDetail.CONTACT_TYPES.twitter,
        6 : ContactDetail.CONTACT_TYPES.facebook,
    }
    RESOURCES_CONTACT_DETAILS = (1,2,5,6)
    RESOURCES_LINKS = (3,4)

    def __init__(self, logger=None):
        if logger:
            self.logger = logger

    def import_op_area(self, op_loc, logger=None):
        """
        Imports a single Area from an openpolis location.
        Imports province acronym and op_location_id as other_identifiers

        @param OpLocation op_loc  instance of territori.models.OpLocation
        @param Logger logger      optional logger object, uses console logger as default

        @return Area              instance of imported Area
        """
        if logger:
            self.logger = logger

        classification = op_loc.location_type.name
        name = op_loc.name
        identifier = self.get_identifier_string_from_op_loc(op_loc)

        area_defaults = {
            'name': name,
            'classification': classification,
        }
        a, created = Area.objects.get_or_create(
            identifier=identifier,
            defaults=area_defaults
        )
        if created:
            self.logger.info(u"Area created: {0} ({1}) - {2}".format(
                name, classification, identifier
            ))
        else:
            # modifica di tutti i campi del progetto, in base ai valori del CSV
            for key, value in area_defaults.items():
                setattr(a, key, value)
            a.save()
            self.logger.info(u"Area found and updated: {0} ({1}) - {2}".format(
                name, classification, identifier
            ))

        #
        # other identifiers
        #

        # openpolis location id
        op_other_identifier, created = Identifier.objects.get_or_create(
            scheme='http://www.openpolis.it/schemas/op-location-id',
            identifier=op_loc.id
        )
        if created:
            self.logger.info(u"Identifier created: {0}".format(op_other_identifier))
        a.other_identifiers.add(op_other_identifier)

        # province acronym
        if classification == 'Provincia':
            prov_other_identifier, created = Identifier.objects.get_or_create(
                scheme='http://www.istat.it/sigle-province(???)',
                identifier=op_loc.prov
            )
            if created:
                self.logger.info(u"Identifier created: {0}".format(prov_other_identifier))

            a.other_identifiers.add(prov_other_identifier)

        # return the imported Area
        return a

    def get_identifier_string_from_op_loc(self, op_loc):
        """
        Returns the identifier string, starting from the OpLocation object
        ex: /OP/italia/reg:ID_REG/prov:ID_PROV/city:ID_CITY

        @param OpLocation op_loc   instance of territori.models.OpLocation

        @return string             the identifier string
        """
        # main identifier
        eu_identifier = "/OP/europa"
        it_identifier = "/OP/italia"

        reg_identifier = ''
        prov_identifier = ''
        identifier = ''

        classification = op_loc.location_type.name

        if classification in ['Regione', 'Provincia', 'Comune']:
            reg_identifier = "{0}/reg:{1}".format(it_identifier, op_loc.regional_id)
            if classification == 'Regione':
                identifier = reg_identifier

        if classification in ['Provincia', 'Comune']:
            prov_identifier = "{0}/prov:{1}".format(reg_identifier, op_loc.provincial_id)
            if classification == 'Provincia':
                identifier = prov_identifier

        if classification == 'Comune':
            identifier = "{0}/city:{1}".format(prov_identifier, op_loc.city_id)

        if classification == 'Europa':
            identifier = eu_identifier

        if classification == 'Italia':
            identifier = it_identifier

        return identifier

    def import_op_politician(self, op_pol, logger=None):
        """
        Imports a single Person from an openpolis politician.

        @param OpPolitician op_pol  instance of territori.models.OpPolitician
        @param Logger logger        optional logger object, uses console logger as default

        @return Person              instance of imported Person
        """

        op_id = op_pol.content_id

        p = Person()

        gender = None
        if op_pol.sex:
            gender = op_pol.sex

        birth_date = op_pol.birth_date.strftime('%Y-%m-%d') if op_pol.birth_date else ''
        death_date = op_pol.death_date.strftime('%Y-%m-%d') if op_pol.death_date else ''

        name = u"{0} {1}".format(op_pol.first_name.lower().capitalize(), op_pol.last_name.lower().capitalize())
        sort_name = u"{0} {1}".format(op_pol.last_name.lower(), op_pol.first_name.lower())

        op_politician_identifier, created = Identifier.objects.get_or_create(
            scheme='http://www.openpolis.it/schemas/op-politician-id',
            identifier=op_id
        )
        if created:
            self.logger.info(u"Identifier created: {0}".format(op_politician_identifier))

        person_defaults = {
            'name': name,
            'given_name': op_pol.first_name,
            'family_name': op_pol.last_name,
            'sort_name': sort_name,
            'birth_date': birth_date,
            'death_date': death_date,
            'gender': gender,
        }

        # create a new Person only if not already imported
        created = False
        person, created = Person.objects.get_or_create(
            identifiers__scheme=op_politician_identifier.scheme,
            identifiers__identifier=op_politician_identifier.identifier,
            defaults=person_defaults
        )

        if created:
            self.logger.info(u"Person created: {0} - {1}".format(
                name, op_politician_identifier
            ))
            person.identifiers.add(op_politician_identifier)
        else:
            # modifica di tutti i campi del progetto, in base ai valori del CSV
            for key, value in person_defaults.items():
                setattr(person, key, value)
            person.save()
            self.logger.info(u"Person found and updated: {0} - {1}".format(
                name, op_politician_identifier
            ))


        #
        # adding contact details from OpResources
        #
        op_pol_resources = OpResources.objects.using('politici').filter(
            politician=op_pol,
            resources_type_id__in=self.RESOURCES_CONTACT_DETAILS
        )

        for op_resource in op_pol_resources:
            if op_resource.descrizione==None:
                descrizione=""
            else:
                descrizione=op_resource.descrizione

            contact, created = ContactDetail.objects.get_or_create(
                contact_type=self.RESOURCES_TYPE_MAP[op_resource.resources_type_id],
                value=op_resource.valore,
                content_type=ContentType.objects.get_for_model(Person),
                object_id=person.id,
                defaults={
                    'label': descrizione
                }
            )
            person.contact_details.add(contact)

        #
        # adding links from OpResources
        #
        op_pol_resources = OpResources.objects.using('politici').filter(
            politician_id=op_id,resources_type_id__in=self.RESOURCES_LINKS)

        for op_resource in op_pol_resources:
            if op_resource.descrizione==None:
                descrizione=""
            else:
                descrizione=op_resource.descrizione

            link, created = Link.objects.get_or_create(
                url=op_resource.valore,
                content_type=ContentType.objects.get_for_model(Person),
                object_id=person.id,
                defaults={
                    'note':descrizione
                }
            )
            person.links.add(link)

        #
        # adding politici.openpolis.it link as source
        #
        link, created = Source.objects.get_or_create(
            url="http://politici.openpolis.it/politico/{0}".format(op_id),
            content_type=ContentType.objects.get_for_model(Person),
            object_id=person.id,
            defaults={
                'note':'Pagina del politico su Openpolis'
            }
        )
        person.sources.add(link)

        # return the imported Person instance
        return person