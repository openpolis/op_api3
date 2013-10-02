# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LocationType'
        db.create_table(u'locations_locationtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'locations', ['LocationType'])

        # Adding model 'AlternativeName'
        db.create_table(u'locations_alternativename', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
        ))
        db.send_create_signal(u'locations', ['AlternativeName'])

        # Adding model 'Code'
        db.create_table(u'locations_code', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'locations', ['Code'])

        # Adding model 'Location'
        db.create_table(u'locations_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('location_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.LocationType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, null=True, blank=True)),
            ('acronym', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('gps_lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('gps_lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('inhabitants_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('inhabitants_male', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('inhabitants_female', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_start', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_end', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('reason_end', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('parent_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'], null=True, blank=True)),
        ))
        db.send_create_signal(u'locations', ['Location'])

        # Adding M2M table for field new_location_set on 'Location'
        db.create_table(u'locations_location_new_location_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_location', models.ForeignKey(orm[u'locations.location'], null=False)),
            ('to_location', models.ForeignKey(orm[u'locations.location'], null=False))
        ))
        db.create_unique(u'locations_location_new_location_set', ['from_location_id', 'to_location_id'])


    def backwards(self, orm):
        # Deleting model 'LocationType'
        db.delete_table(u'locations_locationtype')

        # Deleting model 'AlternativeName'
        db.delete_table(u'locations_alternativename')

        # Deleting model 'Code'
        db.delete_table(u'locations_code')

        # Deleting model 'Location'
        db.delete_table(u'locations_location')

        # Removing M2M table for field new_location_set on 'Location'
        db.delete_table('locations_location_new_location_set')


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
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'gps_lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'gps_lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
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
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['locations']