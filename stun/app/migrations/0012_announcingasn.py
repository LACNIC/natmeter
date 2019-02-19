# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_stunmeasurement_already_processed'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnouncingAsn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asn', models.IntegerField(default=0, null=True)),
                ('ip_address', models.ForeignKey(to='app.StunIpAddress')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
