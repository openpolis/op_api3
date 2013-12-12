# -*- coding: utf-8 -*-
import json
from optparse import make_option
import logging
from StringIO import StringIO
from couchdb import Server
from django.conf import settings
from django.core.management.base import BaseCommand
import requests

__author__ = 'guglielmo'



class Command(BaseCommand):
    """
    Exports all data to a remote CouchDB
    """
    help = "Export all data to a remote CouchDB"

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    dest='dryrun',
                    action='store_true',
                    default=False,
                    help='Set the dry-run command mode: no actual import is made'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to start from'),
    )

    logger = logging.getLogger('import')
    db = None
    counter = 0

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

        self.offset = int(options['offset'])
        self.limit = int(options['limit'])

        self.logger.info("Starting export!")
        server = Server()
        if 'maps-places' not in server:
            self.db = server.create('maps-places')
        else:
            self.db = server['maps-places']

        # places uri startup
        places_uri = "{0}/maps/places".format(settings.OP_API_URI)
        self.logger.debug("GET {0}".format(places_uri))

        # get all places, following the next link
        places_json = self.export_page(places_uri)
        while places_json and places_json['next']:
            places_json = self.export_page(places_json['next'])


    def export_page(self, places_uri):
        r = requests.get(places_uri)
        if r.status_code != 200:
            self.logger.error(u'Error parsing {0}. Skipping.'.format(places_uri))
            exit()
        places_json = r.json()

        for place in places_json['results']:
            self.counter += 1
            if self.counter < self.offset:
                continue
            if self.limit and self.counter > self.offset + self.limit:
                return None
            place_uri = place['_self']
            r = requests.get(place_uri)
            if r.status_code != 200:
                self.logger.error(u'Error parsing {0}. Skipping.'.format(place_uri))
                continue
            place_json = r.json()
            slug = place_json['slug']
            _self = place_json.pop('_self')
            if slug not in self.db:
                self.db[slug]  = place_json
                self.logger.debug("{0}: GET {1}. Created.".format(self.counter, place_uri))
            else:
                self.logger.debug("{0}: GET {1}. Found.".format(self.counter, place_uri))
                #    place_db = self.db[slug]
                #    place_json['_rev'] = place_db.rev
                #    self.db[slug] = place_json

        return places_json


