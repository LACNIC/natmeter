# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 23:22
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20160602_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='StunIpAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(default='127.0.0.1')),
            ],
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='active',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='candidate',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='generation',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='hash',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='host',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='ip_address',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='length',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='number',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='number2',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='protocol',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='sequence',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='sequence2',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='tcptype',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='typ',
        ),
        migrations.RemoveField(
            model_name='stunmeasurement',
            name='ufrag',
        ),
        migrations.AddField(
            model_name='stunmeasurement',
            name='tester_version',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='client_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 2, 23, 22, 15, 751766, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='stunmeasurement',
            name='server_test_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 2, 23, 22, 15, 751718, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='stunipaddress',
            name='stun_measurement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.StunMeasurement'),
        ),
    ]
