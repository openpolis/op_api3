# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LocationGIS'
        db.create_table(u'locations_locationgis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['locations.Location'], unique=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('gps_lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('gps_lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'locations', ['LocationGIS'])

        # Deleting field 'Location.gps_lat'
        db.delete_column(u'locations_location', 'gps_lat')

        # Deleting field 'Location.gps_lon'
        db.delete_column(u'locations_location', 'gps_lon')

        # Deleting field 'Location.geom'
        db.delete_column(u'locations_location', 'geom')


    def backwards(self, orm):
        # Deleting model 'LocationGIS'
        db.delete_table(u'locations_locationgis')

        # Adding field 'Location.gps_lat'
        db.add_column(u'locations_location', 'gps_lat',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.gps_lon'
        db.add_column(u'locations_location', 'gps_lon',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Location.geom'
        db.add_column(u'locations_location', 'geom',
                      self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True),
                      keep_default=False)


    models = {
        u'locations.alternativename': {
            'Meta': {'object_name': 'AlternativeName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'locations.code': {
            'Meta': {'object_name': 'Code'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'locations.location': {
            'Meta': {'object_name': 'Location'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inhabitants_female': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'inhabitants_male': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'inhabitants_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.LocationType']"}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'new_location_set': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'old_location_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['locations.Location']"}),
            'parent_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'reason_end': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'locations.locationgis': {
            'Meta': {'object_name': 'LocationGIS'},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'gps_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gps_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['locations.Location']", 'unique': 'True'})
        },
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['locations']