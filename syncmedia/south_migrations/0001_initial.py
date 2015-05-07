# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Host'
        db.create_table('syncmedia_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=9922, max_length=40)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('pubkey', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('syncmedia', ['Host'])


    def backwards(self, orm):
        # Deleting model 'Host'
        db.delete_table('syncmedia_host')


    models = {
        'syncmedia.host': {
            'Meta': {'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '9922', 'max_length': '40'}),
            'pubkey': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['syncmedia']