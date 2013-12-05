
from django.core.management.base import BaseCommand
from SPARQLWrapper import SPARQLWrapper, JSON

from optparse import make_option
import logging

from places.models import Language


class Command(BaseCommand):
    """
    Language codes are imported from dbpedia.org through a sparql query
    """
    help = "Import language codes from dbpedia"

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual import is made'),
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

        self.logger.info("Inizio import")


        # fetch results from dbpedia.org
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""

        PREFIX dbpprop: <http://dbpedia.org/property/>

        SELECT ?resource ?code ?name
        WHERE {
            ?resource dbpprop:iso ?code .
            ?resource dbpprop:name ?name
            FILTER( regex(?code, "^..$", "i"))
        }
        ORDER BY ?code ?name
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()


        c = 0
        for result in results["results"]["bindings"]:
            # increment counter, to be shown in import log
            c += 1

            iso_code = result["code"]['value']
            name = result["name"]['value']
            resource_uri = result["resource"]['value']

            if not dryrun:
                lang_code, created = Language.objects.get_or_create(
                    dbpedia_resource=resource_uri,
                    defaults={
                        'iso639_1_code': iso_code,
                        'name': name,
                    }
                )
                if created:
                    self.logger.info(u"%d - CREATED %s;%s;%s" % (c, iso_code, name, resource_uri))
                else:
                    self.logger.info(u"%d - MODIFIED %s;%s;%s" % (c, iso_code, name, resource_uri))
            else:
                    self.logger.info(u"%d - READ %s;%s;%s" % (c, iso_code, name, resource_uri))

        self.logger.info("Fine")






