# -*- coding: utf-8 -*-
import json
from optparse import make_option
import logging
from StringIO import StringIO
import pprint
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
    Geometric polygons are
    imported from the open_coesione DB.
    """
    help = "Import polygons from open_coesione database"

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

    logger = logging.getLogger('management')



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


        offset = int(options['offset'])
        limit = int(options['limit'])

        self.logger.info("Starting polygons import!")

        conn = psycopg2.connect("{0}".format(settings.OC_PG_CONN))
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = "select cod_com, denominazione, ST_AsGeoJSON(geom, 12, 0) as geom" +\
              "  from territori_territorio" +\
              "  where territorio ='C' "

        if args:
            sql += " and cod_com in ({0})".format(",".join(args))

        if limit:
            sql += " offset {0} limit {1}".format(offset, limit)
        else:
            sql += " offset {0}".format(offset)

        cursor.execute(sql)
        print "********"
        print "********"
        print "********"
        print "{0}".format(sql)
        print "********"
        print "********"
        print "********"
        print "********"

        oc_places = cursor.fetchall()
        for c, oc_place in enumerate(oc_places):
            self.logger.info(u"{0} - cod_com: {cod_com}, it: {denominazione}".format(c, **oc_place))
            places_uri = "{0}/maps/places?external_id=istat-city-id:{1}".format(
                settings.OP_API_URI, oc_place['cod_com'],
                auth=(settings.OP_API_USERNAME, settings.OP_API_PASSWORD)
            )
            self.logger.debug("{0}: GET {1}".format(c, places_uri))

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
            self.logger.debug("{0}: GET {1}".format(
                c,place_uri, auth=(settings.OP_API_USERNAME, settings.OP_API_PASSWORD)))
            r = requests.get(place_uri)
            if r.status_code != 200:
                self.logger.error(u'Error parsing {0}. Skipping.'.format(place_uri))
                continue

            gps_lat = None
            gps_lon = None
            place_json = r.json()

            if 'geoinfo' in place_json and place_json['geoinfo']:
                if 'geom' in place_json['geoinfo'] and \
                        place_json['geoinfo']['geom']:
                    self.logger.debug("  - geom already found. Skipping")
                    continue

                if 'gps_lat' in place_json['geoinfo']:
                    gps_lat = place_json['geoinfo']['gps_lat']
                if 'gps_lon' in place_json['geoinfo']:
                    gps_lon = place_json['geoinfo']['gps_lon']

            geoinfo = {
                "geoinfo": {
                    "gps_lat": gps_lat,
                    "gps_lon": gps_lon,
                    "geom": oc_place["geom"]
                }
            }

            io = StringIO()
            json.dump(geoinfo, io)

            patch_resp = requests.patch(place_uri, data=io,
                auth=(settings.OP_API_USERNAME, settings.OP_API_PASSWORD),
                headers={'content-type': 'application/json'}
            )
            self.logger.info("  - PATCH {0} - {1}".format(place_uri, patch_resp.status_code))
