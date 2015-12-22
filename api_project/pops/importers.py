import logging
from autoslug.utils import slugify
from django.contrib.contenttypes.models import ContentType
from politici.models import OpResources
from popolo.models import Identifier, Area, ContactDetail, Person, Link, Source, Organization, Post, Membership, \
    OtherName
from territori.models import OpLocation

__author__ = 'guglielmo'

class OpImporterException(Exception):
    pass

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

    REGIONS_ARTICLES = {
      'della ': ("valle d'aosta", 'lombardia', 'liguria',
                      'toscana', 'campania', 'puglia', 'basilicata',
                      'calabria', 'sicilia', 'sardegna'),
      'del ': ("piemonte", "trentino alto adige", "veneto", "friuli venezia giulia",
              "lazio", "molise"),
      'delle ': ('marche', ),
      "dell'": ('abruzzo', 'umbria', 'emilia romagna')
    }

    def __init__(self, logger=None):
        if logger:
            self.logger = logger


    #
    # Helper methods
    #
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


    def get_istat_code_from_op_loc(self, op_loc):
        istat_code = ''
        classification = op_loc.location_type.name
        if classification == 'Comune':
            istat_code = "{:d}{:06d}".format(
                op_loc.regional_id, op_loc.city_id
            )
        elif classification == 'Provincia':
            istat_code = "{:d}{:d}".format(
                op_loc.regional_id, op_loc.provincial_id
            )
        elif classification == 'Regione':
            istat_code = "{:d}".format(op_loc.regional_id)
        else:
            pass
        return istat_code



    def get_full_location_name(self, op_loc):
        """
        Returns the finest full name of an area, given the openpolis location object
        Area object.

        @param string classification  institution classification (e.g. Consiglio Comunale|Comune)
        @param OpLocation object  op_loc
        @return string  The full name
        """

        # perfezionare, prendendo i dati da http://it.wikipedia.org/wiki/Citt%C3%A0_d%27Italia
        # attraverso dbpedia? (vedi places/management/commands/maps_import_languages)
        classification = op_loc.location_type.name
        area_name = op_loc.name
        if 'comun' in classification.lower() or \
           'provinc' in classification.lower():
            if area_name == "L'Aquila":
                full_name = u"{0} dell'Aquila".format(
                    classification,
                )
            elif area_name == "La Spezia":
                full_name = u"{0} della Spezia".format(
                    classification,
                )
            else:
                full_name = u"{0} di {1}".format(
                    classification, area_name
                )

        elif 'region' in classification.lower():
            article = [k for k,v in self.REGIONS_ARTICLES.items() if area_name.lower() in v][0]
            full_name = u"{0} {1}{2}".format(
                classification, article, area_name
            )

        else:
            full_name = u"{0} {1}".format(
                area_name
            )

        return full_name


    def get_full_institution_name(self, classification, area_name, founding_date=None):
        """
        Returns the finest full name of an institution, given the openpolis
        institution name (classification) and the Area name.
        If the founding datre is given, then the year is added to the name.

        Maps all exceptions, plurals, and various other things (in the future)

        @param string classification  institution classification (e.g. Consiglio Comunale|Comune)
        @param string area_name       The area name
        @param date   founding_date
        @return string                The full name
        """
        # perfezionare, prendendo i dati da http://it.wikipedia.org/wiki/Citt%C3%A0_d%27Italia
        # attraverso dbpedia? (vedi places/management/commands/maps_import_languages)
        if 'comun' in classification.lower() or \
           'provinc' in classification.lower():
            if area_name == "L'Aquila":
                institution_name = u"{0} dell'Aquila".format(
                    classification,
                )
            elif area_name == "La Spezia":
                institution_name = u"{0} della Spezia".format(
                    classification,
                )
            else:
                institution_name = u"{0} di {1}".format(
                    classification, area_name
                )

        elif 'regionale' in classification.lower():
            article = [k for k,v in self.REGIONS_ARTICLES.items() if area_name.lower() in v][0]
            institution_name = u"{0} {1}{2}".format(
                classification, article, area_name
            )

        else:
            institution_name = u"{0} {1}".format(
                classification,
                area_name
            )

        if founding_date:
            institution_name = u"{0} - {1}".format(institution_name, founding_date.year)

        return institution_name


    #
    # Import methods
    #
    def import_op_area(self, op_loc, logger=None):
        """
        Imports a single Area from an openpolis location.
        Imports province acronym, op_location_id  and mapit urls as other_identifiers

        @param OpLocation op_loc  instance of territori.models.OpLocation
        @param Logger logger      optional logger object, uses console logger as default

        @return Area              instance of imported Area
        """
        if logger:
            self.logger = logger

        classification = op_loc.location_type.name
        name = op_loc.name
        identifier = self.get_istat_code_from_op_loc(op_loc)
        inhabitants = op_loc.inhabitants

        area_defaults = {
            'name': name,
            'classification': classification,
            'inhabitants': inhabitants,
            'start_date': op_loc.date_start,
            'end_date': op_loc.date_end,
        }
        a, created = Area.objects.get_or_create(
            identifier=identifier,
            defaults=area_defaults
        )
        if created:
            self.logger.debug(u"Area created: {0} ({1}) - {2}".format(
                name, classification, identifier
            ))
        else:
            for key, value in area_defaults.items():
                setattr(a, key, value)
            a.save()
            self.logger.debug(u"Area found and updated: {0} ({1}) - {2}".format(
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
            self.logger.debug(u"Identifier created: {0}".format(op_other_identifier))
        a.other_identifiers.add(op_other_identifier)


        # ISTAT code
        istat_code_type = "ISTAT_{0}".format(classification[0:3].upper())
        istat_code_value = a.identifier

        # mapit url
        mapit_base_endpoint = "http://mapit.openpolis.it"

        if istat_code_value:
            mapit_url = "{0}/code/{1}/{2}.html".format(
                mapit_base_endpoint,
                istat_code_type, istat_code_value
            )
            op_other_identifier, created = Identifier.objects.get_or_create(
                scheme=mapit_base_endpoint,
                identifier=mapit_url
            )
            if created:
                self.logger.debug(u"Identifier created: {0}".format(op_other_identifier))
            a.other_identifiers.add(op_other_identifier)

        # province acronym
        if classification == 'Provincia':
            prov_other_identifier, created = Identifier.objects.get_or_create(
                scheme='http://www.istat.it/sigle-province(???)',
                identifier=op_loc.prov
            )
            if created:
                self.logger.debug(u"Identifier created: {0}".format(prov_other_identifier))

            a.other_identifiers.add(prov_other_identifier)

        # MinInt Electoral codes
        op_other_identifier, created = Identifier.objects.get_or_create(
            scheme='http://amministratori.interno.it/amministratori/AmmIndex7.htm',
            identifier=op_loc.minint_id.strip('None')
        )
        if created:
            self.logger.debug(u"Identifier created: {0}".format(op_other_identifier))
        a.other_identifiers.add(op_other_identifier)

        # return the imported Area
        return a


    def import_op_person(self, op_pol, logger=None):
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
            self.logger.debug(u"Identifier created: {0}".format(op_politician_identifier))

        person_defaults = {
            'name': name,
            'given_name': op_pol.first_name,
            'family_name': op_pol.last_name,
            'sort_name': sort_name,
            'birth_date': birth_date,
            'death_date': death_date,
            'gender': gender,
            'image': "http://politici.openpolis.it/politician/picture?content_id={0}".format(op_id)
        }

        # create a new Person only if not already imported
        created = False
        person, created = Person.objects.get_or_create(
            identifiers__scheme=op_politician_identifier.scheme,
            identifiers__identifier=op_politician_identifier.identifier,
            defaults=person_defaults
        )

        if created:
            self.logger.debug(u"Person created: {0} - {1}".format(
                name, op_politician_identifier
            ))
            person.identifiers.add(op_politician_identifier)
        else:
            # modifica di tutti i campi del progetto, in base ai valori del CSV
            for key, value in person_defaults.items():
                setattr(person, key, value)
            person.save()
            self.logger.debug(u"Person found and updated: {0} - {1}".format(
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


    def import_op_organization(self, op_inst, area, founding_date, dissolution_date=None, logger=None):
        """
        Imports a single Organization from an openpolis institution (and an Area).

        @param OpInstitution op_inst    instance of territori.models.OpPolitician
        @param Area area                instance of Area
        @param date founding_date       the start date (needed)
        @param date dissolution_date    the end date (optional)
        @param Logger logger            optional logger object, uses console logger as default
        @return Person                  instance of imported Person
        """
        classification = op_inst.name
        institution_name = self.get_full_institution_name(classification, area.name, founding_date)

        institution, created = Organization.objects.get_or_create(
            classification=op_inst.name,
            area=area,
            founding_date=founding_date,
            defaults={
                'name' : institution_name,
                'dissolution_date': dissolution_date,
            }
        )

        if created:
            self.logger.debug(u"Institution {0} created.".format(institution_name))
        else:
            # organization name is saved only if changed
            if institution.name != institution_name:
                institution.name = institution_name
                institution.save()
            self.logger.debug(u"Institution {0} found.".format(institution_name))
        return institution


    def import_op_party(self, op_charge):
        """
        Imports a single Organization as a Party.

        @param OpInstitutionCharge op_charge    instance of OpInstitutionCharge model (already normalized)
        @return Organization       instance of imported Organization
        """
        if op_charge.party.name == 'Non specificato' or \
           op_charge.party.name is None or \
           op_charge.party.name.strip() == '':
            return None

        op_party = op_charge.party.getNormalized()
        party, created = Organization.objects.get_or_create(
            classification='Partito o lista di elezione',
            name=op_party.name,
        )

        # party acronym
        if op_party.acronym:
            acronym, created = OtherName.objects.get_or_create(
                note='Acronimo',
                name=op_party.acronym
            )
            party.other_names.add(acronym)

        return party


    def import_op_post(self, op_charge_type, institution, area, logger=None):
        """
        Imports a single Ppost from an openpolis op_charge_type (an Organization and an Area).

        @param OpChargeType op_charge_type  instance of territori.models.OpChargeType
        @param Organization institution     instance of Organization
        @param Area area                    instance of Area
        @param Logger logger                optional logger object, uses console logger as default
        @return Person              instance of imported Person
        """

        role = op_charge_type.name
        label = ""
        if area.classification == 'Comune':
            role = "{0} del comune".format(role)
        elif area.classification == 'Provincia':
            role = "{0} della provincia".format(role)
        elif area.classification == 'Regione':
            role = "{0} della regione".format(role)
        label = self.get_full_institution_name(role, area.name)


        post, created = Post.objects.get_or_create(
            organization=institution,
            area=area,
            role=role,
            defaults={
                'label': label,
            }
        )

        if created:
            self.logger.debug(u"Post {0} created.".format(label))
        else:
            self.logger.debug(u"Post {0} found.".format(label))

        return post

    def import_op_membership(self, op_charge, organization, person, area,
                             post=None, role=None, on_behalf_of=None, logger=None):
        """
        Imports a single Membership from an openpolis op_charge, and
        a Post, an Organization, a Person and an Area

        @param OpCharge op_charge         instance of territori.models.OpChargeType
        @param Post post                  instance of Post (optional)
        @param Organization organization  instance of Organization
        @param Person person              instance of Person
        @param Area area                  instance of Area
        @param Area post                  instance of Post
        @param Area role                  instance of Role
        @param Area on_behalf_of          instance of Organization
        @param Logger logger              optional logger object, uses console logger as default
        @return Membership                instance of imported Membership
        """

        start_date = 'NA'
        end_date = 'NA'
        if op_charge.date_start:
            start_date = op_charge.date_start.strftime("%Y-%m-%d")
        if op_charge.date_end:
            end_date = op_charge.date_end.strftime("%Y-%m-%d")
        if op_charge.date_end is not None:
            label_suffix = u"dal {0} al {1}".format(
                start_date, end_date
            )
        else:
            label_suffix = u"in carica"

        if role is not None:
            label = u"{0} {1}".format(role, label_suffix)
        else:
            if post:
                role = post.label
                label = u"{0} {1}".format(post.label, label_suffix)
            else:
                role = op_charge.charge_type.name
                label = ""
                if area.classification == 'Comune':
                    role = "{0} del comune".format(role)
                elif area.classification == 'Provincia':
                    role = "{0} della provincia".format(role)
                elif area.classification == 'Regione':
                    role = "{0} della regione".format(role)
                label = u"{0} {1}".format(
                    self.get_full_institution_name(role, area.name),
                    label_suffix
                )

        membership_defaults = {
            'role': role,
            'label': label,
            'area': area,
            'on_behalf_of': on_behalf_of,
            'start_date': start_date,
            'end_date': end_date
        }

        membership, created = Membership.objects.get_or_create(
            post=post,
            organization=organization,
            person=person,
            defaults=membership_defaults
        )

        if created:
            self.logger.debug(u"Membership {0} created.".format(label))
        else:
            # modifica di tutti i campi
            for key, value in membership_defaults.items():
                setattr(membership, key, value)
            membership.save()
            self.logger.debug(u"Membership {0} found and updated.".format(label))

        return membership
