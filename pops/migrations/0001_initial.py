# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Person'
        db.create_table(u'pops_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('birth_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('death_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('birth_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Location'], null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('minint_aka', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, blank=True)),
        ))
        db.send_create_signal(u'pops', ['Person'])

        # Adding model 'AlternativeName'
        db.create_table(u'pops_alternativename', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Person'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'pops', ['AlternativeName'])

        # Adding model 'Code'
        db.create_table(u'pops_code', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Person'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'pops', ['Code'])

        # Adding model 'Profession'
        db.create_table(u'pops_profession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'pops', ['Profession'])

        # Adding model 'PersonHasProfession'
        db.create_table(u'pops_personhasprofession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Person'])),
            ('profession', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Profession'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pops', ['PersonHasProfession'])

        # Adding model 'EducationLevel'
        db.create_table(u'pops_educationlevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'pops', ['EducationLevel'])

        # Adding model 'PersonHasEducationLevel'
        db.create_table(u'pops_personhaseducationlevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Person'])),
            ('education_level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.EducationLevel'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pops', ['PersonHasEducationLevel'])

        # Adding model 'ContactType'
        db.create_table(u'pops_contacttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'pops', ['ContactType'])

        # Adding model 'Contact'
        db.create_table(u'pops_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.Person'])),
            ('contact_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pops.ContactType'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pops', ['Contact'])


    def backwards(self, orm):
        # Deleting model 'Person'
        db.delete_table(u'pops_person')

        # Deleting model 'AlternativeName'
        db.delete_table(u'pops_alternativename')

        # Deleting model 'Code'
        db.delete_table(u'pops_code')

        # Deleting model 'Profession'
        db.delete_table(u'pops_profession')

        # Deleting model 'PersonHasProfession'
        db.delete_table(u'pops_personhasprofession')

        # Deleting model 'EducationLevel'
        db.delete_table(u'pops_educationlevel')

        # Deleting model 'PersonHasEducationLevel'
        db.delete_table(u'pops_personhaseducationlevel')

        # Deleting model 'ContactType'
        db.delete_table(u'pops_contacttype')

        # Deleting model 'Contact'
        db.delete_table(u'pops_contact')


    models = {
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
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'pops.alternativename': {
            'Meta': {'object_name': 'AlternativeName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Person']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'pops.code': {
            'Meta': {'object_name': 'Code'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Person']"})
        },
        u'pops.contact': {
            'Meta': {'object_name': 'Contact'},
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.ContactType']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Person']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'pops.contacttype': {
            'Meta': {'object_name': 'ContactType'},
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pops.educationlevel': {
            'Meta': {'object_name': 'EducationLevel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'pops.person': {
            'Meta': {'ordering': "('-modified', '-created')", 'object_name': 'Person'},
            'birth_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'birth_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'death_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'educationlevel_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['pops.EducationLevel']", 'null': 'True', 'through': u"orm['pops.PersonHasEducationLevel']", 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'minint_aka': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'picture': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'profession_set': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['pops.Profession']", 'null': 'True', 'through': u"orm['pops.PersonHasProfession']", 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        u'pops.personhaseducationlevel': {
            'Meta': {'object_name': 'PersonHasEducationLevel'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'education_level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.EducationLevel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Person']"})
        },
        u'pops.personhasprofession': {
            'Meta': {'object_name': 'PersonHasProfession'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Person']"}),
            'profession': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pops.Profession']"})
        },
        u'pops.profession': {
            'Meta': {'object_name': 'Profession'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pops']