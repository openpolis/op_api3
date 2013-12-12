# -*- coding: utf-8 -*-
import json
from optparse import make_option
import logging
from StringIO import StringIO
from django.conf import settings
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from django.core.management.base import BaseCommand
import requests

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


__author__ = 'guglielmo'



class Command(BaseCommand):
    """
    Municipalities having a german name are
    imported from the open_coesione DB.

    Their names and slug are substituted,
    Their german names are added as I18Names
    """
    help = "Import multilingual places from open_coesione database"

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


        self.logger.info("Inizio import nomi teutonici!")

        conn = psycopg2.connect("{0}".format(settings.OC_PG_CONN))
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = "select cod_com, denominazione, denominazione_ted " +\
              "  from territori_territorio " +\
              "  where denominazione_ted is not null " +\
              "        and denominazione_ted != ''"
        if args:
            sql += "and cod_com in ({0})".format(",".join(args))
        cursor.execute(sql)

        oc_places = cursor.fetchall()
        for oc_place in oc_places:
            self.logger.info(u"cod_com: {cod_com}, it: {denominazione}, de: {denominazione_ted}".format(**oc_place))
            places_uri = "{0}/maps/places?external_id=istat-city-id:{1}".format(settings.OP_API_URI, oc_place['cod_com'])
            self.logger.debug("GET {0}".format(places_uri))

            r = requests.get(places_uri)
            if r.status_code != 200:
                self.logger.error(u'Error parsing {0}. Skipping.'.format(places_uri))
                continue

            places_json = r.json()
            if places_json['count'] == 0:
                self.logger.error(u'No places fount at {0}. Skipping.'.format(places_uri))
                continue

            if places_json['count'] > 1:
                self.logger.error(u'More than one places found ({0}) at {1}. Skipping.'.format(places_json['count'], places_uri))
                continue

            place_uri = places_json['results'][0]['_self']
            self.logger.debug("GET {0}".format(place_uri))
            r = requests.get(place_uri)
            if r.status_code != 200:
                self.logger.error(u'Error parsing {0}. Skipping.'.format(place_uri))
                continue


            names = {
                "names": [
                    { "language": "{0}/maps/languages/it".format(settings.OP_API_URI),
                      "name": u"{0}".format(oc_place['denominazione']) },
                    { "language": "{0}/maps/languages/de".format(settings.OP_API_URI),
                      "name": u"{0}".format(oc_place['denominazione_ted']) }
                ]
            }

            names_io = StringIO()
            json.dump(names, names_io)

            self.logger.debug("PATCH {0}".format(places_uri))
            patch_resp = requests.patch(place_uri, data=names_io,
                auth=(settings.OP_API_USERNAME, settings.OP_API_PASSWORD),
                headers={'content-type': 'application/json'}
            )
            self.logger.debug(patch_resp.status_code)
