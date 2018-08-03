# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StunIpAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.GenericIPAddressField(default='127.0.0.1')),
                ('ip_address_kind', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StunIpAddressChangeEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('previous', models.GenericIPAddressField(default='127.0.0.1')),
                ('current', models.GenericIPAddressField(default='127.0.0.1')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StunMeasurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_test_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('client_test_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('experiment_id', models.TextField(default='')),
                ('cookie', models.TextField(default='', null=True)),
                ('tester_version', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stunipaddresschangeevent',
            name='stun_measurement',
            field=models.ForeignKey(to='app.StunMeasurement'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stunipaddress',
            name='stun_measurement',
            field=models.ForeignKey(to='app.StunMeasurement'),
            preserve_default=True,
        ),
    ]
