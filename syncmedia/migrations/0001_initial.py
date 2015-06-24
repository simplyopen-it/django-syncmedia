# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=256)),
                ('url', models.CharField(unique=True, max_length=256)),
                ('port', models.IntegerField(default=9922, max_length=40)),
                ('username', models.CharField(max_length=256, null=True, blank=True)),
                ('pubkey', models.CharField(max_length=512)),
                ('sync_dirs', django_extensions.db.fields.json.JSONField(default=b'[]', null=True, blank=True)),
                ('root_path', models.CharField(default=b'/home/marco/workspace/usatravelvisa', max_length=512, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
